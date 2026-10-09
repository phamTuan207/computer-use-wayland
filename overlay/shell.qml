import QtQuick
import Quickshell
import Quickshell.Io
import Quickshell.Wayland

ShellRoot {
  PanelWindow {
    id: panel
    property bool active: false
    visible: active
    implicitWidth: 282
    implicitHeight: 38
    anchors { top: true }
    margins.top: 8
    color: "transparent"
    exclusionMode: ExclusionMode.Ignore
    focusable: false
    WlrLayershell.namespace: "agent-computer-use"
    WlrLayershell.layer: WlrLayer.Overlay
    mask: Region { width: 0; height: 0 }

    Timer {
      id: expiry
      interval: 30000
      onTriggered: {
        panel.active = false
        hotkeyOff.running = true
      }
    }

    IpcHandler {
      target: "computerUse"
      function activate(): void { panel.active = true; expiry.restart() }
      function suspend(): void { panel.active = false }
      function restore(): void { panel.active = true }
      function deactivate(): void {
        panel.active = false
        expiry.stop()
        hotkeyOff.running = true
      }
    }

    Rectangle {
      anchors.fill: parent
      radius: height / 2
      color: "#701b1e24"
      border.color: "#78d7dce0"
      border.width: 1

      Rectangle {
        x: 13; anchors.verticalCenter: parent.verticalCenter
        width: 6; height: 6; radius: 3
        color: "#9bbaa9"
      }
      Text {
        x: 28; anchors.verticalCenter: parent.verticalCenter
        text: "Computer-use active"
        color: "#eef0f2"
        font.family: "Noto Sans"
        font.pixelSize: 12
        font.weight: Font.Medium
      }
      Rectangle {
        x: 174; anchors.verticalCenter: parent.verticalCenter
        width: 1; height: 16
        color: "#5a73777d"
      }
      Text {
        x: 186
        anchors.verticalCenter: parent.verticalCenter
        text: "Esc to cancel"
        color: "#c9cdd1"
        font.family: "Noto Sans"
        font.pixelSize: 11
      }
    }

    Process {
      id: hotkeyOff
      command: ["python3", "scripts/overlayctl.py", "hotkey-off"]
    }
  }
}
