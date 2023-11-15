@echo off
:start
ECHO.
ECHO 1. Run Server
ECHO 2. Run Client1
ECHO 3. Run Client2
ECHO 4. Run Client2 + Client3
ECHO 5. Run Main
ECHO 6. Quit
set choice=
set /p choice=Type the number to run file: 
if not '%choice%'=='' set choice=%choice:~0,1%
if '%choice%'=='1' goto Server
if '%choice%'=='2' goto Client1
if '%choice%'=='3' goto Client2
if '%choice%'=='4' goto Client23
if '%choice%'=='5' goto Main
if '%choice%'=='6' goto Quit
ECHO "%choice%" is not valid, try again
ECHO.
goto start
:Server
cd %cd%\Server
start py Server.py
cd ..
goto start
:Client1
cd %cd%\Client_1
start py Client.py
cd ..
goto start
:Client2
cd %cd%\Client_2
start py Client.py
cd ..
goto start
:Client23
cd %cd%\Client_2
start py Client.py
cd ..
cd %cd%\Client_3
start py Client.py
cd ..
goto start
:Main
cd %cd%\Client_1
start py Main.py
cd ..
goto start
:Quit