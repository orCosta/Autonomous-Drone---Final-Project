DEBUG:
http://python.dronekit.io/develop/sitl_setup.html
PC:
	on cmd run: 
	>dronekit-sitl copter 
	for huji start pos run: 
	>dronekit-sitl copter-3.3 --home=31.774077,35.198426,584,353
		
	for hebrew-academy	:
	>dronekit-sitl copter-3.3 --home=31.772290, 35.198167,584,353
	
	to connet with the MissionPlanner use: TCP 127.0.0.1 port 5762 or port 5763
	
R-pi:
	use: 
	vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True)	
	
	
