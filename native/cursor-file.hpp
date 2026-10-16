#pragma once
#include <cstdint>
#include <filesystem>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <cerrno>
#include <stdexcept>
#include <vector>

// Decode only an immutable, bounded copy. Validate dimensions before libXcursor
// allocates pixels, rather than discovering an oversized image afterwards.
inline std::vector<char> cursorFile(const std::filesystem::path& path) {
    const int fd = open(path.c_str(), O_RDONLY | O_NONBLOCK | O_CLOEXEC);
    if (fd < 0) throw std::runtime_error("cursor file unavailable");
    std::vector<char> bytes;
    try {
        struct stat info{};
        if (fstat(fd, &info) || !S_ISREG(info.st_mode) || info.st_size < 16 || info.st_size > 16 * 1024 * 1024)
            throw std::runtime_error("cursor file exceeds bounds or is not regular");
        bytes.resize(static_cast<size_t>(info.st_size));
        size_t offset = 0;
        while (offset < bytes.size()) {
            const auto count = read(fd, bytes.data()+offset, bytes.size()-offset);
            if (count < 0 && errno == EINTR) continue;
            if (count <= 0) throw std::runtime_error("cursor file read failed");
            offset += static_cast<size_t>(count);
        }
    } catch (...) { close(fd); throw; }
    close(fd);
    auto word = [&](size_t offset) -> uint32_t {
        if (offset > bytes.size() - 4) throw std::runtime_error("truncated cursor header");
        uint32_t value = 0;
        for (unsigned i = 0; i < 4; ++i) value |= static_cast<uint32_t>(static_cast<unsigned char>(bytes[offset+i])) << (8*i);
        return value;
    };
    const auto header = word(4), count = word(12);
    if (word(0) != 0x72756358 || header != 16 || word(8) != 0x10000 || !count || count > 256 ||
        static_cast<uint64_t>(header) + 12ULL * count > bytes.size())
        throw std::runtime_error("invalid cursor table");
    bool image = false;
    for (uint32_t i = 0; i < count; ++i) {
        const size_t entry = header + 12ULL*i;
        if (word(entry) != 0xfffd0002) continue;
        const uint64_t offset = word(entry+8);
        if (offset + 36 > bytes.size()) throw std::runtime_error("truncated cursor image");
        const uint64_t imageHeader = word(offset), width = word(offset+16), height = word(offset+20);
        if (word(offset+4) != 0xfffd0002 || word(offset+8) != word(entry+4) || imageHeader != 36 || word(offset+12) != 1 ||
            !width || !height || width > 1024 || height > 1024 || word(offset+24) >= width || word(offset+28) >= height ||
            offset + imageHeader + width*height*4 > bytes.size())
            throw std::runtime_error("invalid or oversized cursor image");
        image = true;
    }
    if (!image) throw std::runtime_error("cursor contains no image");
    return bytes;
}
