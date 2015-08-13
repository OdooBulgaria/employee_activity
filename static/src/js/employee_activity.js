openerp.employee_activity = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    local.activity_document = instance.Widget.extend({
    	template:"activity_employee",
    	events:{
    		'click .create_new':"add_activity_line",
    		'click .toggle_match.glyphicon.glyphicon-play':"show_activities",
			'click .toggle_create.glyphicon.glyphicon-play':"hide_activities"	
    	},
    	init:function(parent,employee_id,employee_name,project_id,activities){
    		this._super(parent);
    		this.employee_id = employee_id;
    		this.employee_name = employee_name;
    		this.project_id = project_id;
    		this.activities = activities;
    		var defs = [];
    		this.lines_object = [];
    		this.blank_line = {
                   	'id':null,
    				'site_id':"",
                	'site_name':"",
                	'remarks':"",
                	'distance_site_location':"",
                	'daily_allowance':"",
                	'current_location':"",
                	'local_conveyance':"",
                	'reporting_time_site':false,
                	'return_time_site':false,
                	'travelling_allowance':"",
                	'lodging':"",
                	'state':"wip",
    		}
    	},
    	show_activities:function(event){
    		var self = this;
    		$(event.srcElement).removeClass('toggle_match');
    		$(event.srcElement).addClass('toggle_create');
    		_.each(self.lines_object,function(line){
    			line.$el.show();
    		});
    	},
    	hide_activities:function(event){
    		var self = this;
    		$(event.target).removeClass('toggle_create');
    		$(event.target).addClass('toggle_match');    		
    		_.each(self.lines_object,function(line){
    			line.$el.hide();
    		});
    	},    	
    	add_activity_line:function(){
    		var self = this
			activity_line = new local.activity_line(self,self.employee_id,self.blank_line,self.employee_name,self.project_id,"create");
    		activity_line.prependTo(self.$el).done(activity_line.createFormWidgets());
    		activity_line.on("create_render_widget",this,function(id,activity_line){
    			activity_line.destroy();
    			var activity_line = new openerp.Model('employee.activity.line');
    			activity_line.call('read', [id,[]]).then(function (result) {
    				new_line = new local.activity_line(self,self.employee_id,result,self.employee_name,self.project_id,"edit");
    	    		new_line.appendTo(self.$el).done(new_line.createFormWidgets());    				
    	    		self.lines_object.push(new_line);
    			});
			});
    	},
    	
    	start:function(){
    		var self = this;
    		var tmp = this._super();
    		_.each(self.lines_object,function(line){
    			defs.push(line.appendTo(self.$el).done(function(){
    				line.createFormWidgets();
    				line.$el.hide();	
				}))
			})
    		return $.when(tmp,defs)
    	},
    	
    	renderElement:function(){
    		var self = this;
    		this._super();
            var $document= $(QWeb.render("table-caption", {
                "name": self.employee_name
            }));
            return $.when($document.prependTo(self.$el)).then(function(){
            	_.each(self.activities,function(line){
        			activity_line = new local.activity_line(self,self.employee_id,line,self.employee_name,self.project_id,"edit");
        			self.lines_object.push(activity_line)
        		});    	    		            	
            })
    	}
    });
    
    local.activity_line = instance.Widget.extend({
    	events : {
    		"click span.toggle_match.glyphicon.glyphicon-play":"open_line_form",
    		"click span.toggle_create.glyphicon.glyphicon-play":"close_line_form",
    		"click .save_changes":"save_changes",
			"click .create_cancel":"create_cancel",
    	},
    	init:function(parent,employee_id,line,employee_name,project_id,mode){
    		this._super(parent);
    		this.parent = parent;
    		this.mode = mode; // if mode = create then create widget
    		this.employee_id = employee_id;
    		this.project_id = project_id;
    		this.employee_name = employee_name
    		this.line = line
            this.$super_container = null;
    		this.create_form_fields = {
					work_description:{
	                   id: "work_description",
	                    index: 0,
	                    corresponding_property: "work_description", // a account.move field name
	                    label: _t("Work Description"),
	                    required: true,
	                    tabindex: 10,
	                    constructor: instance.web.form.FieldMany2One,
	                    field_properties: {
	                    	relation: "project.description.line",
	                        string: _t("Work Description"),
	                        type: "many2one",
	                    },
					},
    				site_name:{
                        id: "site_name",
                        index: 1,
                        corresponding_property: "site_name",
                        label: _t("Site Name"),
                        required: true,
                        tabindex: 11,
                        constructor: instance.web.form.FieldChar,
                        field_properties: {
                            string: _t("Site Name"),
                            type: "char",
                        },    					
    				},
    				site_id:{
                        id: "site_id",
                        index: 2,
                        corresponding_property: "site_id",
                        label: _t("Site ID"),
                        required: true,
                        tabindex: 11,
                        constructor: instance.web.form.FieldChar,
                        field_properties: {
                            string: _t("Site ID"),
                            type: "char",
                        },    					
    				},    				
    				current_location:{
                        id: "current_location",
                        index: 3,
                        corresponding_property: "current_location",
                        label: _t("Current Location"),
                        required: true,
                        tabindex: 11,
                        constructor: instance.web.form.FieldChar,
                        field_properties: {
                            string: _t("Current Location"),
                            type: "char",
                        },    					
    				},
    				state: {
                        id: "state",
                        index: 4,
                        corresponding_property: "state",
                        label: _t("Status"),
                        required: true,
                        tabindex: 11,
                        constructor: instance.web.form.FieldSelection,
                        field_properties: {
                            string: _t("Status"),
                            type: "selection",
                            selection:[
                                       ['completed','Completed'],
                                       ['uncompleted','Not Completed'],
                                       ['wip',"WIP"],
                                       ['unattempted',"Not Attempted"],
                                       ],
                        },
                    },
                    local_conveyance: {
                        id: "local_conveyance",
                        index: 5,
                        corresponding_property: "local_conveyance",
                        label: _t("Local Conveyance"),
                        required: true,
                        tabindex: 13,
                        constructor: instance.web.form.FieldFloat,
                        field_properties: {
                            string: _t("Local Conveyance"),
                            type: "float",
                        },
                    },
					activity_line:{
		                   id: "activity_line",
		                    index: 6,
		                    corresponding_property: "activity_line", // a account.move field name
		                    label: _t("Activity"),
		                    required: true,
		                    tabindex: 10,
		                    constructor: instance.web.form.FieldMany2One,
		                    field_properties: {
		                        relation: "activity.line",
		                        string: _t("Activity"),
		                        type: "many2one",
		                    },
						},
    				remarks: {
                        id: "remarks",
                        index: 7,
                        corresponding_property: "remarks",
                        label: _t("Remarks"),
                        required: true,
                        tabindex: 11,
                        constructor: instance.web.form.FieldChar,
                        field_properties: {
                            string: _t("Remarks"),
                            type: "char",
                        },
                    },						
                    reporting_time_site: {
                        id: "reporting_time_site",
                        index: 7,
                        corresponding_property: "reporting_time_site",
                        label: _t("Reporting Time"),
                        required: true,
                        tabindex: 11,
                        constructor: instance.web.form.FieldDatetime,
                        field_properties: {
                            string: _t("Reporting Time"),
                            type: "datetime",
                        },
                    },
                    return_time_site:{
                        id: "return_time_site",
                        index: 8,
                        corresponding_property: "return_time_site",
                        label: _t("Returning Time"),
                        required: true,
                        tabindex: 11,
                        constructor: instance.web.form.FieldDatetime,
                        field_properties: {
                            string: _t("Returning Time"),
                            type: "datetime",
                        },
                    },
                    distance_site_location: {
                        id: "distance_site_location",
                        index: 9,
                        corresponding_property: "distance_site_location",
                        label: _t("Distance from Site Location"),
                        required: true,
                        tabindex: 13,
                        constructor: instance.web.form.FieldFloat,
                        field_properties: {
                            string: _t("Distance from Site Location"),
                            type: "float",
                        },
                    },                    
                    travelling_allowance: {
                        id: "travelling_allowance",
                        index: 10,
                        corresponding_property: "travelling_allowance",
                        label: _t("Travelling Allowance Applied (TA)"),
                        required: true,
                        tabindex: 13,
                        constructor: instance.web.form.FieldFloat,
                        field_properties: {
                            string: _t("Travelling Allowance Applied (TA)"),
                            type: "float",
                        },
                    },                                        
                    daily_allowance: {
                        id: "daily_allowance",
                        index: 11,
                        corresponding_property: "daily_allowance",
                        label: _t("Daily Allowance Applied (TA)"),
                        required: true,
                        tabindex: 13,
                        constructor: instance.web.form.FieldFloat,
                        field_properties: {
                            string: _t("Daily Allowance Applied (TA)"),
                            type: "float",
                        },
                    },                                                            
                    lodging: {
                        id: "lodging",
                        index: 11,
                        corresponding_property: "lodging",
                        label: _t("Lodging"),
                        required: true,
                        tabindex: 13,
                        constructor: instance.web.form.FieldFloat,
                        field_properties: {
                            string: _t("Lodging"),
                            type: "float",
                        },
                    },                                                                                
                };
    	},
    	create_cancel:function(){
    		this.destroy();
    	},
    	save_changes:function(event){
    		var self = this
    		activity_line = new openerp.Model('employee.activity.line');
    		if (self.mode == "edit"){
        		activity_line.call('write', [self.line.id,{
        			'site_id':self.line.site_id,
                	'site_name':self.line.site_name,
                	'remarks':self.line.remarks,
                	'distance_site_location':self.line.distance_site_location,
                	'daily_allowance':self.line.daily_allowance,
                	'current_location':self.line.current_location,
                	'local_conveyance':self.line.local_conveyance,
                	'reporting_time_site':self.line.reporting_time_site,
                	'return_time_site':self.line.return_time_site,
                	'travelling_allowance':self.line.travelling_allowance,
                	'lodging':self.line.lodging,
                }]).then(function(){
            	self.$el.find('.toggle_create').click();
                })    			
    		}
    	   if (self.mode == "create"){
    		   console.log(self.line);
    		   activity_line.call('create', [{
       			'activity_line':self.line.activity_line,
       			'work_description':self.line.work_description,
       			'project_id':self.project_id[0],
       			'employee_id':self.employee_id,
       			'site_id':self.line.site_id,
            	'site_name':self.line.site_name,
            	'remarks':self.line.remarks,
            	'distance_site_location':self.line.distance_site_location,
            	'daily_allowance':self.line.daily_allowance,
            	'current_location':self.line.current_location,
            	'local_conveyance':self.line.local_conveyance,
            	'reporting_time_site':self.line.reporting_time_site,
            	'return_time_site':self.line.return_time_site,
            	'travelling_allowance':self.line.travelling_allowance,
            	'lodging':self.line.lodging,
    		    'state':self.line.state,	
    		   }]).then(function(id){
    			   	self.trigger("create_render_widget",id,self)
    		   	})     		   
    	   	}
    	},
    	createFormWidgets: function(mode) {
    		/* 
    		 * takes in the mode create or save and then renders accordingly
    		 */
    		var self = this;
            var create_form_fields = self.create_form_fields;
            var create_form_fields_arr = [];
            for (var key in create_form_fields)
                if (create_form_fields.hasOwnProperty(key))
                    create_form_fields_arr.push(create_form_fields[key]);
            create_form_fields_arr.sort(function(a, b){ return b.index - a.index });
    
            // field_manager
            var dataset = new instance.web.DataSet(this, "employee.activity.line", self.context);
            dataset.ids = [];
            dataset.arch = {
                attrs: { string: "Employee Activities", version: "7.0", class: "oe_form_container" },
                children: [],
                tag: "form"
            };
    
            var field_manager = new instance.web.FormView (
                this, dataset, false, {
                    initial_mode: 'edit',
                    disable_autofocus: false,
                    $buttons: $(),
                    $pager: $()
            });
    
            field_manager.load_form(dataset);
    
            // fields default properties
            var Default_field = function() {
                this.context = {};
                this.domain = [];
                this.help = "";
                this.readonly = false;
                this.required = true;
                this.selectable = true;
                this.states = {};
                this.views = {};
            };
            var Default_node = function(field_name) {
                this.tag = "field";
                this.children = [];
                this.required = true;
                this.attrs = {
                    invisible: "False",
                    modifiers: '{"required":true}',
                    name: field_name,
                    nolabel: "True",
                };
            };
    
            // Append fields to the field_manager
            field_manager.fields_view.fields = {};
            for (var i=0; i<create_form_fields_arr.length; i++) {
                field_manager.fields_view.fields[create_form_fields_arr[i].id] = _.extend(new Default_field(), create_form_fields_arr[i].field_properties);
            }
            // Returns a function that serves as a xhr response handler
            // generate the create "form"
            self.create_form = [];
            var $super_container = $(QWeb.render("super_container", {'mode':self.mode}));
            for (var i=0; i<create_form_fields_arr.length; i++) {
                var field_data = create_form_fields_arr[i];
                // create widgets
                var node = new Default_node(field_data.id);
                if (! field_data.required) node.attrs.modifiers = "";
                var field = new field_data.constructor(field_manager, node);
                self[field_data.id+"_field"] = field;
                self.create_form.push(field);
                field.set_value(self.line[field.name]);
                
                if (self.mode != "create" && (field.name == "work_description" || field.name == "activity_line")  ){
                	field.modifiers.readonly = true;
                }
                // on update : change the last created line
                field.corresponding_property = field_data.corresponding_property;
                
                field.on("change:value",self,function(event){
                	self.line[event.name] = event.get("value");
                });
    
                // append to DOM
                var $field_container = $(QWeb.render("form_create_field_employee_activity", {id: field_data.id, label: field_data.label}));
                field.appendTo($field_container.find("td"));
                $super_container.find('div.oe_form').prepend($field_container);
    
                // now that widget's dom has been created (appendTo does that), bind events and adds tabindex
                if (field_data.field_properties.type != "many2one") {
                    // Triggers change:value TODO : moche bind ?
                    field.$el.find("input").keyup(function(e, field){ field.commit_value(); }.bind(null, null, field));
                }
                field.$el.find("input").attr("tabindex", field_data.tabindex);
    
                // Hide the field if group not OK
                if (field_data.group !== undefined) {
                    var target = $field_container;
                    target.hide();
                    self.model_res_users
                        .call("has_group", [field_data.group])
                        .then(hideGroupResponseClosureFactory(field, target, (field_data.id+"_field")));
                }
            }
            // generate the change partner "form"
            if (self.mode == "create"){
            	$super_container.show();
            	self.$el.find('tr.line').hide();
            }
            self.$el.find("tbody.container").append($super_container);
            self.$super_container = $super_container;
            self.field_manager = field_manager;
            field_manager.do_show();
            return $.when();
    	},
    
    	renderElement:function(){
    		var self = this;
    		self.$el.append($(QWeb.render("activity_line", {'widget':{'line':self.line}})));
    	},
    	open_line_form:function(event){
    		var self = this
    		$(event.srcElement).removeClass('toggle_match');
    		$(event.srcElement).addClass('toggle_create');
    		self.$super_container.show("300ms");
    	},
    	close_line_form:function(event){
    		var self = this
    		$(event.target).removeClass('toggle_create');
    		$(event.target).addClass('toggle_match');
    		self.$super_container.hide("300ms");
    	},
    	start:function(){
    		var self = this;
    		return this._super();
    	},
    });
    
    local.action_plan = instance.Widget.extend({
    	template:"activity_document",
    	init:function(parent){
    		this._super(parent)
    		self.data = null
    	},
    	start: function() {
    		var self =this;
    		defs=[];
            var mod = new instance.web.Model("employee.activity.line");
            defs.push(mod.call("list_employees_activity_data", []).then(function(result) {
        		self.data = result
        		_.each(self.data,function(employee){
        			console.log(employee)
        			// employee.current_project is project_id in all the child widgets called
                    activity_document= new local.activity_document(this,employee.employee_id,employee.name,employee.current_project,employee.activities);
                	activity_document.appendTo(self.$el.find('div.oe_form_sheet.oe_form_sheet_width'))
        		})
        	}));
        	return $.when(defs);          
    	},
    });
    
    instance.web.client_actions.add(
            'local.action_plan', 'instance.employee_activity.action_plan');
}