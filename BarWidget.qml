import QtQuick
import Quickshell.Io
import qs.Ui

BarWidget {
  id: root
  moduleName: "dornkimik.gnome-calendar"

  property string eventTitle: ""
  property string eventStart: ""
  property string statusText: "Kalender lädt…"
  readonly property string scriptPath: decodeURIComponent(Qt.resolvedUrl("scripts/next_event.py").toString().replace(/^file:\/\//, ""))
  readonly property string eventLabel: eventTitle === "" ? statusText :
    Qt.formatDateTime(new Date(eventStart), "dd.MM. HH:mm") + " " + eventTitle
  readonly property string shortLabel: eventLabel.length > 36 ? eventLabel.slice(0, 35) + "…" : eventLabel

  function refresh() {
    if (!readProcess.running) readProcess.running = true
  }

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  Component.onCompleted: refresh()

  Timer {
    interval: 60000
    running: true
    repeat: true
    onTriggered: root.refresh()
  }

  Process {
    id: readProcess
    command: ["/usr/bin/python", root.scriptPath]
    running: false
    stdout: StdioCollector { id: output; waitForEnd: true }
    onExited: function(exitCode) {
      if (exitCode !== 0) {
        root.eventTitle = ""
        root.statusText = "Kalender nicht verfügbar"
        return
      }
      try {
        var result = JSON.parse(output.text)
        root.eventTitle = result.title || ""
        root.eventStart = result.start || ""
        root.statusText = result.status === "empty" ? "Keine Termine" : "Kalender nicht verfügbar"
      } catch (e) {
        root.eventTitle = ""
        root.statusText = "Kalender nicht verfügbar"
      }
    }
  }

  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: root.shortLabel
    tooltipText: root.eventLabel
    onPressed: function(buttonCode) {
      if (buttonCode === Qt.LeftButton && root.bar) root.bar.run("gnome-calendar")
      else if (buttonCode === Qt.MiddleButton) root.refresh()
    }
  }
}
