# droneGestures

Controll Crazyflie Nano Quadcopter by Bitcraze with Leap Motion controller on OS X (Mac)

Die Arbeit wurde als Semesterarbeit an der [ZHAW](http://zhaw.ch) umgesetzt.

## Abstract
In diesem Dokument wird die Umsetzung einer Gestensteuerung für eine Drohne beschrieben. Als Drohne wird der Crazyflie 2.0 Nano Quadcopter von Bitcraze verwendet. Für die Gestenerkennung wird auf den Leap Motion Sensor zurückgegriffen.

Das Hauptziel der Steuerung ist die intuitive Bedienung, die aus einfachen Handgesten abgeleitet werden kann. Die Umsetzung soll die Vorteile, so wie auch möglichen Probleme einer Gestensteuerung aufzeigen. Zusätzlich zur Steuerung, wird auf die Problematik der Initialisierung der Gestensteuerung eingegangen. Wie kann sichergestellt werden, dass unabsichtlich ausgelöste Gesten keine Auswirkungen auf die Drohne haben? Nebst dem Konzept wird eine Umsetzung anhand der Crazyflie und dem Leap Motion Sensor in Python implementiert.

Für die Erarbeitung einer Gestensteuerung ist eine klare Gliederung unabdingbar. So ist zu Beginn eine gründliche Recherche der Beschaffenheit von Quadrocoptern notwendig. Nur so kann anschliessend eine Ist- und eine Soll-Analyse erstellt werden. Aufgrund dieser Analyse lässt sich das Konzept der Gestensteuerung definieren, sowie die auf erster Stufe erkannten Probleme bereits zu eruieren.

Auf der Basis der konkreten Implementierung, welche durch Tests verifiziert wurde, können nun Rückschlüsse auf das Konzept gewonnen werden, wodurch dieses bei Bedarf präzisiert werden kann.

Nur so kann unter Berücksichtigung aller Vor- und Nachteile einer Gestensteuerung eine Schlussfolgerung erarbeitet und ein Fazit gezogen werden.

## Vollständige Dokumentation
Die ganze Dokumentation ist als [PDF](https://github.com/MrJack91/droneGestures/raw/master/doc/drone.pdf) vorhanden.

## Projekt Struktur
Das Projekt besteht aus zwei Teilen: der Dokumentation ([/doc](https://github.com/MrJack91/droneGestures/tree/master/doc)) und der Umsetzung in Pyhton ([/code](https://github.com/MrJack91/droneGestures/tree/master/code)) auf OS X ausführbar.

## Demo
Auf [Youtube](https://youtu.be/dNCrFgdL1TM).
