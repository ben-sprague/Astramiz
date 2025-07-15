# USV Control Stack

## MOOS-IvP (Backseat Controller)
The middleware that will handle message traffic between various parts of the USV will be MOOS (Mission Oriented Opperating Suite)
with MIT's MOOS IvP(<https://moos-ivp.org>) as the basis for the autonomy. It will run on a backseat computer (likley a Raspberry Pi)
and will be responsible for autonomy, path planning, and communication off the USV.

## Frontseat Controller
The frontseat controlled will control the onboard sensors and actuators. It will likley an Arduino (or similar microcontroller) and will communicate with
the backseat computer (likley through a USB serial connection) to provide sensor information and receive actuation commands.

### Sensors
#### AIRMAR WeatherStation 220WX
<https://www.airmar.com/Product/220WX>

- GPS
- Air Temperature 
- Barometric Pressure
- 9 DoF IMU
- Wind Speed and Direction

#### Water Temperature
Exact sensor unknown, needed to calculate the speed of sound for use in SONAR operation

#### Water Salinity
Exact sensor unknown (and may not be needed if constant salinity can be assumed from historical data), needed to calculate
the speed of sound for use in SONAR operation

#### SONAR 
##### Cerulean Omniscan 450 FS Imaging Sonar
<https://bluerobotics.com/store/sonars/imaging-sonars/cerulean-omniscan-450-fs-imaging-sonar/>

- 120m range
- 50 deg horizontal beamwidth
- 0.8 deg vertial beamwidth

##### Ping360 SONAR
- 25 degree vertical beamwidth
- 360 degree mechanically scanned

#### Doppler Velocity Log
Exact sensor unknown. Get speed and course through water to calculate set and drift. This can be done through GPS and dead reconning, 
but will likley be more accurate with a DVL.

#### Camera
Specfics unknown at this time

### Actuators
#### Sail angle
Controlled by a stepper motor

#### Rudder angle
Controlled by a stepper motor
