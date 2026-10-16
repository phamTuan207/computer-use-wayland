// Session-owned cursor pixels. No input interception or global theme changes.
#include <hyprland/src/plugins/PluginAPI.hpp>
#include <hyprland/src/Compositor.hpp>
#include <hyprland/src/pointer/PointerManager.hpp>
#include <hyprland/src/pointer/cursor/CursorManager.hpp>
#include <hyprland/src/render/Renderer.hpp>
#include <hyprland/src/state/MonitorState.hpp>
#include <hyprland/src/protocols/InputCapture.hpp>
#include <nlohmann/json.hpp>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <unistd.h>
#include <cerrno>
#include <cmath>
#include <filesystem>
#include <stdexcept>
#include "cursor-file.hpp"
#define Time X11Time
#include <X11/Xcursor/Xcursor.h>
#undef Time
#undef None

namespace {
using Json = nlohmann::json;
constexpr size_t LIMIT = 4096;
using CursorCache = decltype(Render::IHyprRenderer::m_lastCursorData);

class Guard {
    int listener = -1, peer = -1;
    wl_event_source *listenerEvent = nullptr, *peerEvent = nullptr, *stopEvent = nullptr;
    std::string path, request, token;
    bool active = false, repainting = false, cleanupFailed = false, lockFailure = false, captureHidden = false;
    SP<Pointer::Cursor::CCursorBuffer> image;
    Vector2D hotspot;
    float scale = 1;
    CursorCache underlying;
    CHyprSignalListener cursorChanged, layoutChanged;
    std::vector<PHLMONITORREF> locked;

    static bool hexToken(const std::string& text) {
        return text.size() == 32 && text.find_first_not_of("0123456789abcdef") == std::string::npos;
    }

    static void reply(int fd, const Json& data) {
        const auto bytes = data.dump() + "\n";
        if (send(fd, bytes.data(), bytes.size(), MSG_NOSIGNAL) != static_cast<ssize_t>(bytes.size()))
            throw std::runtime_error("cursor guard acknowledgement failed");
    }

    void restoreImage() {
        if (underlying.surf.has_value()) {
            const auto surface = underlying.surf.value();
            if (surface && !surface->resource()) {
                g_pHyprRenderer->setCursorFromName("left_ptr", true);
                underlying = g_pHyprRenderer->m_lastCursorData;
            } else
                g_pHyprRenderer->setCursorSurface(surface, underlying.hotspotX, underlying.hotspotY, true);
        } else if (!underlying.name.empty())
            g_pHyprRenderer->setCursorFromName(underlying.name, true);
        else
            g_pHyprRenderer->setCursorSurface(nullptr, 0, 0, true);
        // Restore the application's latest cache, including animation metadata.
        g_pHyprRenderer->m_lastCursorData = underlying;
        g_pHyprRenderer->ensureCursorRenderingMode();
    }

    bool release() noexcept {
        if (!active && locked.empty() && !cleanupFailed) return true;
        active = false;
        captureHidden = false;
        cursorChanged.reset();
        layoutChanged.reset();
        cleanupFailed = false;
        try {
            // Hidden client updates can change this cache without emitting
            // cursorChanged. Always restore the latest request, even if the
            // lease ends between capture hide and show.
            underlying = g_pHyprRenderer->m_lastCursorData;
            restoreImage();
        } catch (...) { cleanupFailed = true; }
        for (const auto& weak : locked) {
            try {
                if (auto monitor = weak.lock()) Pointer::mgr()->unlockSoftwareForMonitor(monitor);
            } catch (...) { lockFailure = true; }
        }
        // An exception may follow the decrement. Never decrement twice, and
        // never claim recovery from that uncertain operation without a login.
        locked.clear();
        cleanupFailed = cleanupFailed || lockFailure;
        image.reset();
        return !cleanupFailed;
    }

    void disconnect() noexcept {
        if (stopEvent) { wl_event_source_remove(stopEvent); stopEvent = nullptr; }
        release();
        if (peerEvent) { wl_event_source_remove(peerEvent); peerEvent = nullptr; }
        if (peer >= 0) { close(peer); peer = -1; }
        request.clear();
        if (!cleanupFailed) token.clear();
    }

    void deferDisconnect() noexcept {
        if (stopEvent) return;
        // cursorChanged can run inside an animation loader. Restore named
        // cursors only after that stack has unwound.
        stopEvent = wl_event_loop_add_idle(g_pCompositor->m_wlEventLoop, [](void* data) {
            auto self = static_cast<Guard*>(data);
            self->stopEvent = nullptr;
            self->disconnect();
        }, this);
        if (!stopEvent) {
            // Do not restore a named cursor from an animation stack even when
            // idle allocation fails. Stop the owner; its recovery RPC retries
            // on the event-loop I/O stack, with the original token retained.
            cleanupFailed = true;
            cursorChanged.reset();
            layoutChanged.reset();
            if (peerEvent) { wl_event_source_remove(peerEvent); peerEvent = nullptr; }
            if (peer >= 0) { close(peer); peer = -1; }
        }
    }

    void repaint() {
        if (!active || repainting) return;
        if (PROTO::inputCapture->isCaptured()) { deferDisconnect(); return; }
        // The renderer cache belongs to the client; our temporary image must
        // not replace it, including when the client explicitly hides its cursor.
        underlying = g_pHyprRenderer->m_lastCursorData;
        repainting = true;
        try {
            if (captureHidden)
                g_pHyprRenderer->setCursorHidden(true);
            else {
                auto& cache = g_pHyprRenderer->m_lastCursorData;
                cache.surf = SP<Desktop::View::CWLSurface>{};
                g_pHyprRenderer->setCursorHidden(false);
                // Equal names return after setting m_cursorHasSurface, before
                // the loader. Never nest a loader inside its animation tick.
                cache.name = "cu-session-cursor";
                g_pHyprRenderer->setCursorFromName(cache.name, false);
                Pointer::mgr()->setCursorBuffer(image, hotspot, scale);
            }
            g_pHyprRenderer->m_lastCursorData = underlying;
        } catch (...) {
            g_pHyprRenderer->m_lastCursorData = underlying;
            repainting = false;
            throw;
        }
        repainting = false;
    }

    void acquire(const Json& data) {
        if (cleanupFailed) throw std::runtime_error("cursor guard cleanup required");
        if (!data.is_object() || data.size() != 4 || data.at("schema") != 1 ||
            !data.at("schema").is_number_integer() || !data.at("size").is_number_integer() ||
            !data.at("theme").is_string() || !data.at("token").is_string())
            throw std::runtime_error("invalid cursor guard request");
        const auto theme = data.at("theme").get<std::string>();
        const auto candidate = data.at("token").get<std::string>();
        if (data.at("size") < 16 || data.at("size") > 96)
            throw std::runtime_error("invalid cursor size");
        const int size = data.at("size").get<int>();
        if (!hexToken(candidate) || theme.empty() || theme.size() > 100 || theme == "." || theme == ".." ||
            theme.find_first_not_of("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-") != std::string::npos || size < 16 || size > 96)
            throw std::runtime_error("invalid cursor guard profile");
        if (PROTO::inputCapture->isCaptured()) throw std::runtime_error("input is captured");
        token = candidate;
        scale = 1;
        for (const auto& monitor : State::monitorState()->monitors())
            scale = std::max(scale, static_cast<float>(std::ceil(monitor->m_scale)));
        if (scale > 8) throw std::runtime_error("unsupported cursor scale");
        std::filesystem::path directory;
        const char* roots = XcursorLibraryPath();
        if (!roots) throw std::runtime_error("Xcursor search path unavailable");
        std::string paths(roots);
        for (size_t begin = 0; begin <= paths.size();) {
            const auto end = paths.find(':', begin);
            std::string root = paths.substr(begin, end == std::string::npos ? end : end - begin);
            if (root.starts_with("~/")) {
                const char* home = getenv("HOME");
                if (!home) throw std::runtime_error("HOME unavailable");
                root = std::string(home) + root.substr(1);
            }
            if (!root.empty() && std::filesystem::is_directory(std::filesystem::path(root) / theme)) {
                directory = std::filesystem::path(root) / theme; break;
            }
            if (end == std::string::npos) break;
            begin = end + 1;
        }
        if (directory.empty()) throw std::runtime_error("agent cursor theme unavailable in compositor");
        auto bytes = cursorFile(directory / "cursors/left_ptr");
        FILE* file = fmemopen(bytes.data(), bytes.size(), "rb");
        if (!file) throw std::runtime_error("cursor memory stream unavailable");
        auto decoded = XcursorFileLoadImage(file, static_cast<int>(size * scale));
        fclose(file);
        if (!decoded) throw std::runtime_error("agent cursor image cannot be decoded");
        try {
            if (!decoded->width || !decoded->height || decoded->width > 1024 || decoded->height > 1024 ||
                decoded->xhot >= decoded->width || decoded->yhot >= decoded->height)
                throw std::runtime_error("agent cursor image exceeds bounds");
            image = makeShared<Pointer::Cursor::CCursorBuffer>(reinterpret_cast<const uint8_t*>(decoded->pixels),
                        Vector2D{static_cast<int>(decoded->width), static_cast<int>(decoded->height)}, Vector2D{static_cast<int>(decoded->xhot), static_cast<int>(decoded->yhot)});
            hotspot = Vector2D{static_cast<int>(decoded->xhot), static_cast<int>(decoded->yhot)} / scale;
        } catch (...) { XcursorImageDestroy(decoded); throw; }
        XcursorImageDestroy(decoded);
        underlying = g_pHyprRenderer->m_lastCursorData;
        // Each lock has a matching owner; hotplug must never decrement a new
        // monitor's zero software-lock count.
        for (const auto& monitor : State::monitorState()->monitors()) {
            locked.emplace_back(monitor);
            Pointer::mgr()->lockSoftwareForMonitor(monitor);
        }
        active = true;
        cursorChanged = Pointer::mgr()->m_events.cursorChanged.listen([this] {
            try { repaint(); } catch (...) { deferDisconnect(); }
        });
        layoutChanged = Event::bus()->m_events.monitor.layoutChanged.listen([this] { disconnect(); });
        repaint();
        if (!active || cleanupFailed || peer < 0) throw std::runtime_error("cursor guard lost during startup");
        reply(peer, {{"ok", true}, {"schema", 1}, {"token", token}});
    }

    void readPeer() {
        char bytes[512];
        const auto count = recv(peer, bytes, sizeof(bytes), 0);
        if (count <= 0) {
            if (count == 0 || (errno != EAGAIN && errno != EINTR)) disconnect();
            return;
        }
        if (request.size() + static_cast<size_t>(count) > LIMIT) { disconnect(); return; }
        request.append(bytes, count);
        const auto newline = request.find('\n');
        if (newline == std::string::npos) return;
        if (newline + 1 != request.size()) { disconnect(); return; }
        const auto data = Json::parse(request.substr(0, newline));
        if (active) {
            if (!data.is_object() || data.size() != 2 || data.at("token") != token ||
                !data.at("op").is_string()) throw std::runtime_error("invalid cursor visibility request");
            const auto op = data.at("op").get<std::string>();
            if (op != "hide" && op != "show") throw std::runtime_error("invalid cursor visibility operation");
            captureHidden = op == "hide";
            repaint();
            if (stopEvent || cleanupFailed) throw std::runtime_error("cursor visibility lost");
            reply(peer, {{"ok",true},{"schema",1},{"token",token},{"state",captureHidden ? "hidden" : "visible"}});
        } else acquire(data);
        request.clear();
    }

    static int peerReady(int, uint32_t mask, void* context) {
        auto self = static_cast<Guard*>(context);
        try {
            if (mask & (WL_EVENT_HANGUP | WL_EVENT_ERROR)) self->disconnect();
            else self->readPeer();
        } catch (...) { self->disconnect(); }
        return 0;
    }

    static int acceptPeer(int fd, uint32_t, void* context) {
        auto self = static_cast<Guard*>(context);
        const int accepted = accept4(fd, nullptr, nullptr, SOCK_NONBLOCK | SOCK_CLOEXEC);
        if (accepted < 0) return 0;
        ucred credentials{}; socklen_t length = sizeof(credentials);
        if (self->peer >= 0 || self->active || self->cleanupFailed ||
            getsockopt(accepted, SOL_SOCKET, SO_PEERCRED, &credentials, &length) || credentials.uid != geteuid()) {
            close(accepted); return 0;
        }
        self->peer = accepted;
        self->peerEvent = wl_event_loop_add_fd(g_pCompositor->m_wlEventLoop, accepted, WL_EVENT_READABLE, peerReady, self);
        if (!self->peerEvent) { close(accepted); self->peer = -1; }
        return 0;
    }

  public:
    Guard() {
        const char* runtime = getenv("XDG_RUNTIME_DIR");
        if (!runtime || runtime[0] != '/') throw std::runtime_error("private XDG_RUNTIME_DIR required");
        const auto directory = std::filesystem::path(runtime) / "agent-computer-use";
        if (mkdir(directory.c_str(), 0700) && errno != EEXIST) throw std::runtime_error("cursor guard directory unavailable");
        struct stat info{};
        if (lstat(directory.c_str(), &info) || !S_ISDIR(info.st_mode) || info.st_uid != geteuid() || (info.st_mode & 0777) != 0700)
            throw std::runtime_error("cursor guard directory is not private");
        path = (directory / "cursor-guard.sock").string();
        sockaddr_un address{}; address.sun_family = AF_UNIX;
        if (path.size() >= sizeof(address.sun_path)) throw std::runtime_error("cursor guard path too long");
        if (!lstat(path.c_str(), &info)) {
            if (!S_ISSOCK(info.st_mode) || info.st_uid != geteuid()) throw std::runtime_error("unsafe cursor guard endpoint");
            const int probe = socket(AF_UNIX, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
            if (probe < 0) throw std::runtime_error("cursor guard probe unavailable");
            std::copy(path.begin(), path.end(), address.sun_path);
            const int result = connect(probe, reinterpret_cast<sockaddr*>(&address), sizeof(address));
            const int error = errno;
            close(probe);
            struct stat fresh{};
            if (result == 0 || error != ECONNREFUSED || lstat(path.c_str(), &fresh) || fresh.st_ino != info.st_ino || fresh.st_dev != info.st_dev)
                throw std::runtime_error("cursor guard endpoint already owned");
            if (unlink(path.c_str())) throw std::runtime_error("stale cursor guard endpoint cannot be removed");
        } else if (errno != ENOENT) throw std::runtime_error("cursor guard endpoint cannot be inspected");
        listener = socket(AF_UNIX, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
        if (listener < 0) throw std::runtime_error("cursor guard socket unavailable");
        std::copy(path.begin(), path.end(), address.sun_path);
        if (bind(listener, reinterpret_cast<sockaddr*>(&address), sizeof(address))) {
            close(listener); listener = -1; throw std::runtime_error("cursor guard endpoint cannot bind");
        }
        if (listen(listener, 4)) {
            close(listener); unlink(path.c_str()); listener = -1; throw std::runtime_error("cursor guard listen failed");
        }
        listenerEvent = wl_event_loop_add_fd(g_pCompositor->m_wlEventLoop, listener, WL_EVENT_READABLE, acceptPeer, this);
        if (!listenerEvent) { close(listener); unlink(path.c_str()); listener = -1; throw std::runtime_error("cursor guard event registration failed"); }
    }

    ~Guard() {
        disconnect();
        if (listenerEvent) wl_event_source_remove(listenerEvent);
        if (listener >= 0) close(listener);
        if (!path.empty()) unlink(path.c_str());
    }

    std::string command(std::string request) {
        if (request == "cu-cursor status") return Json{{"ok", !cleanupFailed}, {"schema", 1}, {"active", active}, {"token", token}}.dump();
        constexpr std::string_view prefix = "cu-cursor release ";
        if (!request.starts_with(prefix)) return "invalid cursor guard command";
        const auto expected = request.substr(prefix.size());
        if (!hexToken(expected)) return "invalid cursor guard token";
        if ((active || cleanupFailed) && token != expected) return "cursor guard belongs to another session";
        if (active || cleanupFailed) disconnect();
        return Json{{"ok", !cleanupFailed}, {"schema", 1}, {"released", expected}}.dump();
    }
};

UP<Guard> guard;
}

APICALL EXPORT std::string PLUGIN_API_VERSION() { return HYPRLAND_API_VERSION; }

APICALL EXPORT PLUGIN_DESCRIPTION_INFO PLUGIN_INIT(HANDLE handle) {
    if (std::string(GIT_COMMIT_HASH) != "efb50993780079460b0cbed1363e2166a2de1d9f" ||
        std::string(__hyprland_api_get_hash()) != __hyprland_api_get_client_hash())
        throw std::runtime_error("cursor guard requires pinned Hyprland 0.56.2 ABI");
    guard = makeUnique<Guard>();
    if (!HyprlandAPI::registerHyprCtlCommand(handle, {"cu-cursor", false, [](eHyprCtlOutputFormat, std::string request) {
            try { return guard->command(request); } catch (...) { return std::string("cursor guard cleanup failed"); }
        }})) {
        guard.reset(); throw std::runtime_error("cursor guard command registration failed");
    }
    return {"computer-use-cursor", "Session-owned cursor image lease", "computer-use-wayland", "1.0.0"};
}

APICALL EXPORT void PLUGIN_EXIT() { guard.reset(); }
