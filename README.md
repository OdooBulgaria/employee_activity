# Employee Activities
--------------------------
- [ ] Add tracker_line field 
	- [ ] This field will be required field if it has project_id field. But required modifier will not be applied. It will be a _constraint or ensure in  create or write method
- [ ] Decide for _inherits
	- [ ] i.e. peoject.tracker.line  _inherits employee.activity.line or the other way round. Decide it later if required

## Conditions for creating project.tracker.line
-----------------------------------------------------
- [ ] Check this in create and write method of employee.activity.line
	- [ ] Look for a unique set of (work description,activity_line,site_id,site_name,emplopyee type (inhouse or vendor)
	- [ ] Check it and then create project.tracker.line and update the tracker_line field employee.activity.line or update the existing tracker_line record
	
# Project Tracker
---------------------
- [ ] Create o2m field with project_id (telecom.project,required)
- [ ] Add other related fields and functional field for cost,earnings and margins  
