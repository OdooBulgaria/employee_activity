openerp.employee_activity = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    // Project Tracker Dashboard
    instance.web.views.add('tree_tracker_dashboard', 'instance.web.pls.filter_view_tracker');
    instance.web.pls.filter_view_tracker = instance.web.ListView.extend({
    	init:function(){
            this._super.apply(this, arguments);
            var self = this;
            self.current_project= null;
            self.project_list_sorted = [];
		},
    	start:function(){
    		var self = this;
    		var defs = []
    		self.d = $.Deferred();
            return this._super.apply(this, arguments).then(function(){
            	self.$el.parent().prepend(QWeb.render("project_tracker_dashboard", {widget: this}));
                self.$el.parent().find('.oe_select').change(function() {
                		self.current_project = this.value === '' ? null : parseInt(this.value);
    	                self.do_search(self.last_domain, self.last_context, self.last_group_by);
    	            });            	
            	var mod = new instance.web.Model("telecom.project", self.dataset.context, self.dataset.domain);
                defs.push(mod.call("list_project", []).then(function(result) {
                	self.project = result
                	self.d.resolve();
                }));
                return $.when(defs)
            });  		
    	},
    	
    	do_search:function(domain, context, group_by){
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            self.project_list_sorted = []
            var o;
            self.$el.parent().find('.oe_select').children().remove().end();
            self.$el.parent().find('.oe_select').append(new Option('', ''));
            $.when(self.d).then(function(){
                if (self.project){
                    for (var i = 0;i < self.project.length;i++){
                    	self.project_list_sorted.push(self.project[i][0]);
                    	o = new Option(self.project[i][1], self.project[i][0]);
                        self.$el.parent().find('.oe_select').append(o);
                    }            	
                    self.$el.parent().find('.oe_select')[0].value = self.current_project;
                }                        	
            });
            return self.search_by_project_id();    		
    	},
    	
    	search_by_project_id: function() {
            var self = this;
            var domain = [];
            
            /*
             * Check if the user is a Project Manager,Circle Head of Corporate
             *  - If Project Manager then show all attendances for the project in which the project manager is 
             *  - Corporate Head is able to see attendance of all his projects and the project managers under him 
             *  - Corporate is able to see all
             */
            
            if (self.current_project!== null) domain.push(['project_id','=',self.current_project]);
            else{
            	domain.push(["project_id", "in", self.project_list_sorted]);
            }
            self.last_context["project_id"] = self.current_project === null ? false : self.current_project;
            var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();
            return self.old_search(compound_domain, self.last_context, self.last_group_by);            	
        },            	
    });    

    
    
    
    
    // Activity Dashboard
    instance.web.views.add('tree_activity_dashboard', 'instance.web.pls.filter_view_activities');
    instance.web.pls.filter_view_activities = instance.web.ListView.extend({
    	init:function(){
            this._super.apply(this, arguments);
            var self = this;
            self.date_from = null;
            self.date_to = null;
            self.project_id = null;
            self.circle_id = null;
            self.employee_id = null;
            self.state = "wip";
            self.defs = [];
            self.info = null;
            self.d = $.Deferred();
            self.project_list = [];
            self.circle_list = [];
            self.employee_list = [];
            self.state = null;
            self.render_element = $("");
    	},
    	start:function(){
    		var self = this;
            today_date = (new Date()).format("Y-m-d");
            return this._super.apply(this, arguments).then(function(){
            	var mod = new instance.web.Model("employee.activity.line", self.dataset.context, self.dataset.domain);
                self.defs.push(mod.call("list_caption", []).then(function(result) {
                	self.info = result
                	self.d.resolve();
                }));
            });  		
    	},
    	
    	do_search:function(domain, context, group_by){
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            var o;
            return $.when(self.d).done(function(){
            	self.$el.parent().find("div.oe_account_quickadd.ui-toolbar").remove();
            	self.render_element = 	$(QWeb.render("activity_dashboard", {info: self.info}))
            	$.when(self.$el.parent().prepend(self.render_element)).then(function(){
            			//onchange project,circle,employee
            			self.$el.parent().find('select.clear_group,select.oe_select_selection').change(function() {
                        		self[$(this)[0].id] = this.value === '' ? null : parseInt(this.value) || this.value
                				return self.search_employee_activity_lines();
            	            });
            			//onchange from and to dates
	                      self.$el.parent().find("input.oe_datepicker_pls").change(function(){
	                    	if (this.value !== "") 
	                    		self[$(this)[0].id] = this.value;
	                		else self[$(this)[0].id] = null;
	                    	return self.search_employee_activity_lines();
	                      });
            			//onchange selection fields
	                      
            				self.$el.parent().find('.clear_group').children().remove().end();
	    	                self.$el.parent().find('.clear_group').append(new Option('', ''));
	    	            	// rendering projects
	    	                if (self.info.project){
	    	                    for (var i = 0;i < self.info.project.length;i++){
	    	                    	self.project_list.push(self.info.project[i][0])
	    	                    	o = new Option(self.info.project[i][1], self.info.project[i][0]);
	    	                        self.$el.parent().find('.oe_select_project').append(o);
	    	                    }            	
	    	                    self.$el.parent().find('.oe_select_project')[0].value = self.project_id;
	    	                }
	    	                //render circles
	    	                if (self.info.circle){
	    	                    for (var i = 0;i < self.info.circle.length;i++){
	    	                    	self.circle_list.push(self.info.circle[i][0])
	    	                    	console.log(self.circle_list)
	    	                    	o = new Option(self.info.circle[i][1], self.info.circle[i][0]);
	    	                        self.$el.parent().find('.oe_select_circle').append(o);
	    	                    }            	
	    	                    self.$el.parent().find('.oe_select_circle')[0].value = self.circle_id;
	    	                }	    	     
	    	                //rendering employees
	    	                if (self.info.employee){
	    	                    for (var i = 0;i < self.info.employee.length;i++){
	    	                    	self.employee_list.push(self.info.employee[i][0])
	    	                    	o = new Option(self.info.employee[i][1], self.info.employee[i][0]);
	    	                        self.$el.parent().find('.oe_select_employee_name').append(o);
	    	                    }            	
	    	                    self.$el.parent().find('.oe_select_employee_name')[0].value = self.employee_id;
	    	                }	    	                	    	                
	    	            });            			
            		});
    		},

    		search_employee_activity_lines: function() {
            var self = this;
            var domain = [];
            if (self.info.project){
                if (self.project_id !== null) domain.push(["project_id", "=", self.project_id]);
                else{
                	domain.push(["project_id", "in", self.project_list]);
            	}            	
            }
            if (self.info.circle){
                if (self.circle_id !== null) domain.push(["project_id.circle", "=", self.circle_id]);
                else{
                	domain.push(["project_id.circle", "in", self.circle_list]);
            	}                        	
            }
            if (self.info.employee){
                if (self.employee_id !== null) domain.push(["employee_id", "=", self.employee_id]);
                else{
                	domain.push(["employee_id", "in", self.employee_list]);
            	}                        	
            }
            if (self.state !== null ) domain.push(['state','=',self.state]);
            else{
            	domain.push(['state','in',['completed','uncompleted','wip','unattempted']])
            }
            domain.push(['date','>=',self.date_from || today_date ]);
        	domain.push(['date','<=',self.date_to || today_date ]);
        	var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();
            return self.old_search(compound_domain, self.last_context, self.last_group_by);            	
        },            	
    });
        
    
    
    local.activity_document = instance.Widget.extend({
    	template:"activity_employee",
    	events:{
    		'click .create_new':"add_activity_line",
    		'click .toggle_match_head.glyphicon.glyphicon-play':"show_activities",
			'click .toggle_create_head.glyphicon.glyphicon-play':"hide_activities"	
    	},
    	init:function(parent,employee_id,employee_name,project_id,activities,type){
    		this._super(parent);
    		this.employee_id = employee_id;
    		this.type = type;
    		this.employee_name = employee_name;
    		this.project_id = project_id;
    		this.project_name = project_id[1];
    		this.activities = activities;
    		var defs = [];
    		this.lines_object = [];
    		this.blank_line = {
                   	'id':null,
                	'site_id':false,
                	'remarks':false,
                	'distance_site_location':false,
                	'daily_allowance':false,
                	'current_location':false,
                	'local_conveyance':false,
                	'work_description':false,
                	'activity_line':false,
                	'reporting_time_site':false,
                	'return_time_site':false,
                	'travelling_allowance':false,
                	'lodging':false,
                	'state':"wip",
    		}
    	},
    	show_activities:function(event){
    		var self = this;
    		$(event.srcElement).removeClass('toggle_match_head');
    		$(event.srcElement).addClass('toggle_create_head');
    		_.each(self.lines_object,function(line){
    			line.$el.show("300ms");
    		});
    	},
    	hide_activities:function(event){
    		var self = this;
    		$(event.target).removeClass('toggle_create_head');
    		$(event.target).addClass('toggle_match_head');    		
    		_.each(self.lines_object,function(line){
    			line.$el.hide("300ms");
    		});
    	},    	
    	add_activity_line:function(event){
    		var self = this
    		$(event.currentTarget).removeClass('create_new')  // Do not allow them have multiple create forms for a single employee
    		activity_line = new local.activity_line(self,self.employee_id,self.blank_line,self.employee_name,self.project_id,"create");
    		activity_line.appendTo(self.$el).done(activity_line.createFormWidgets());
    		activity_line.on("create_render_widget",this,function(id,activity_line){
    			self.$el.find("button.name").addClass("create_new");
    			if (!id){
					return;
    			}
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
                "name": self.employee_name,
                "project_id":self.project_id,
                "project_name":self.project_name,
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
    		this.project_name = project_id[1];
    		this.employee_name = employee_name
    		this.line = line
            this.$super_container = null;
    		this.create_form_fields = {
    				work_description:{
	                   id: "work_description",
	                    index: 2,
	                    corresponding_property: "work_description", // a account.move field name
	                    label: _t("Work Description"),
	                    required: true,
	                    tabindex: 0,
	                    constructor: instance.web.form.FieldSelection,
	                    field_properties: {
	                    	relation: "project.description.line",
	                        string: _t("Work Description"),
	                        type: "many2one",
	                        domain:[['project_id','=',this.project_id[0]]],
	                    },
					},
    				site_id:{
                        id: "site_id",
                        index: 3,
                        corresponding_property: "site_id",
                        label: _t("Site"),
                        required: true,
                        tabindex: 1,
                        constructor: instance.web.form.FieldSelection,
                        field_properties: {
                            relation:"project.site",
                        	string: _t("Site"),
                            type: "many2one",
                        },    					
    				},
    				state: {
                        id: "state",
                        index:4 ,
                        corresponding_property: "state",
                        label: _t("Status"),
                        required: true,
                        tabindex: 2,
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
    				current_location:{
                        id: "current_location",
                        index: 5,
                        corresponding_property: "current_location",
                        label: _t("Current Location"),
                        required: true,
                        tabindex: 3,
                        constructor: instance.web.form.FieldChar,
                        field_properties: {
                            string: _t("Current Location"),
                            type: "char",
                        },    					
    				},

                    distance_site_location: {
                        id: "distance_site_location",
                        index: 6,
                        corresponding_property: "distance_site_location",
                        label: _t("Distance from Site Location"),
                        required: true,
                        tabindex: 4,
                        constructor: instance.web.form.FieldFloat,
                        field_properties: {
                            string: _t("Distance from Site Location"),
                            type: "float",
                        },
                    },                    
    				activity_line:{
		                   id: "activity_line",
		                    index: 7,
		                    corresponding_property: "activity_line", // a account.move field name
		                    label: _t("Activity"),
		                    required: true,
		                    tabindex: 5,
		                    constructor: instance.web.form.FieldMany2One,
		                    field_properties: {
		                        relation: "activity.line.line",
		                        string: _t("Activity"),
		                        type: "many2one",
		                        domain:[['line_id.activity_line.description_id','=',false]],
		                    },
						},
	    				site_code:{
	                        id: "site_code",
	                        index: 8,
	                        corresponding_property: "site_code",
	                        label: _t("Site ID"),
	                        required: true,
	                        tabindex: 6,
	                        constructor: instance.web.form.FieldChar,
	                        field_properties: {
	                        	string: _t("Site ID"),
	                            type: "char",
	                    	},    					
	    				},    				
						
					remarks: {
                        id: "remarks",
                        index: 9,
                        corresponding_property: "remarks",
                        label: _t("Remarks"),
                        required: true,
                        tabindex: 7,
                        constructor: instance.web.form.FieldChar,
                        field_properties: {
                            string: _t("Remarks"),
                            type: "char",
                        },
                    },						
                    reporting_time_site: {
                        id: "reporting_time_site",
                        index: 10,
                        corresponding_property: "reporting_time_site",
                        label: _t("Reporting Time"),
                        required: true,
                        tabindex: 8,
                        constructor: instance.web.form.FieldDatetime,
                        field_properties: {
                            string: _t("Reporting Time"),
                            type: "datetime",
                        },
                    },
                    return_time_site:{
                        id: "return_time_site",
                        index: 11,
                        corresponding_property: "return_time_site",
                        label: _t("Returning Time"),
                        required: true,
                        tabindex: 9,
                        constructor: instance.web.form.FieldDatetime,
                        field_properties: {
                            string: _t("Returning Time"),
                            type: "datetime",
                        },
                    },
                    local_conveyance: {
                        id: "local_conveyance",
                        index: 12,
                        corresponding_property: "local_conveyance",
                        label: _t("Local Conveyance"),
                        required: true,
                        tabindex: 10,
                        constructor: instance.web.form.FieldFloat,
                        field_properties: {
                            string: _t("Local Conveyance"),
                            type: "float",
                        },
                    },

                    travelling_allowance: {
                        id: "travelling_allowance",
                        index: 13,
                        corresponding_property: "travelling_allowance",
                        label: _t("Travelling Allowance(TA)"),
                        required: true,
                        tabindex: 11,
                        constructor: instance.web.form.FieldFloat,
                        field_properties: {
                            string: _t("Travelling Allowance(TA)"),
                            type: "float",
                        },
                    },                                        
                    daily_allowance: {
                        id: "daily_allowance",
                        index: 14,
                        corresponding_property: "daily_allowance",
                        label: _t("Daily Allowance Applied (DA)"),
                        required: true,
                        tabindex: 12,
                        constructor: instance.web.form.FieldFloat,
                        field_properties: {
                            string: _t("Daily Allowance Applied (TA)"),
                            type: "float",
                        },
                    },                                                            
                    lodging: {
                        id: "lodging",
                        index: 15,
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
                    multiple_employees:{
 	                   id: "multiple_employees",
	                    index: 16,
	                    corresponding_property: "multiple_employees", // a account.move field name
	                    label: _t("Replicate Activity"),
	                    required: true,
	                    tabindex: 14,
	                    constructor: instance.web.form.FieldMany2ManyTags,
	                    field_properties: {
	                    	relation: "hr.employee",
	                        string: _t("Replicate Activity"),
	                        type: "many2many",
	                        domain:[['emp_type','=',parent.type],['id','!=',employee_id]],
	                    },                    	
                    },
                };
    	},
    	create_cancel:function(){
    		this.trigger("create_render_widget",false,this);
    		this.destroy();
    	},
    	rerender_caption:function(line){
    		var self = this;
    		self.$el.find("tr.line").replaceWith($(QWeb.render("activity_line", {'widget':{'line':self.line},'glyphicon':'create'})))
    	},
    	save_changes:function(event){
    		var self = this
    		activity_line = new openerp.Model('employee.activity.line');
    		if (self.mode == "edit"){
    			activity_line.call('write', [self.line.id,{
    				'site_id':self.site_id_field.get("value"),
                	'remarks':self.remarks_field.get("value"),
                	'distance_site_location':self.distance_site_location_field.get("value"),
                	'daily_allowance':self.daily_allowance_field.get("value"),
                	'current_location':self.current_location_field.get("value"),
                	'local_conveyance':self.local_conveyance_field.get("value"),
                	'reporting_time_site':self.reporting_time_site_field.get("value"),
                	'return_time_site':self.return_time_site_field.get("value"),
                	'travelling_allowance':self.travelling_allowance_field.get("value"),
                	'lodging':self.lodging_field.get("value"),
        		}]).then(function(){
        			self.rerender_caption(self.line);
        			self.$el.find('.toggle_create').click();
                })    			
    		}
    	   
    		if (self.mode == "create"){
    		   if (!self.line.activity_line || !self.line.work_description){
    			   alert("You are required to assign an activity and work description");
    			   return;
			   
    		   } 
    		   activity_line.call('create', [{
       			'activity_line':self.line.activity_line || false,
       			'work_description':self.line.work_description || false,
       			'project_id':self.project_id[0],
       			'employee_id':self.employee_id,
       			'site_id':self.line.site_id,
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
                    $pager: $(),
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
                if (field_data.id == 'multiple_employees' && self.mode == 'edit'){
                	continue;
                }
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
                	self.line[event.name] =  event.get("value");
                	if (event.name == 'work_description'){
                		self.activity_line_field.set_value(false);
                		self.activity_line_field.field.domain = [['site_id','=',self.site_id_field.get("value")],['type','=',self.parent.type],['line_id.activity_line.description_id','=',self.line.work_description]]
                			
                	}
                	if (event.name == 'site_id'){
                		model = new openerp.Model('project.site');
                		self.activity_line_field.field.domain = [['site_id','=',self.site_id_field.get("value")],['type','=',self.parent.type],['line_id.activity_line.description_id','=',self.line.work_description]]
                		if (event.get("value") && typeof(event.get("value")) == "number"){
                    		self.line[event.name] = event.get("value"); //working
                			model.call('read',[event.get("value"),['site_id']]).done(function(result){
                				self.site_code_field.set_value(result.site_id || "Site Code Not Defined");
                			});
                		}
                		
                	}
                	self.line[event.name] = event.get("value");
                });
    
                // append to DOM
                var $field_container = $(QWeb.render("form_create_field_employee_activity", {id: field_data.id, label: field_data.label}));
                if (field_data.id == 'multiple_employees') {
                	$field_container.find('td').css('width','150px')
                }
                field.appendTo($field_container.find("td"));
                $super_container.find('div.oe_form').prepend($field_container);
    
                // now that widget's dom has been created (appendTo does that), bind events and adds tabindex
                if (field_data.field_properties.type != "many2one") {
                    // Triggers change:value TODO : moche bind ?
                    field.$el.find("input").keyup(function(e, field){ field.commit_value(); }.bind(null, null, field));
                }
                if (field.name == 'state'){
                	console.log(field.$el.find("select[name='state']"));
                	field.$el.keyup(function(e,field){
                		if (e.keyCode == 9){
                			e.preventDefault();
                		}
                	})
                
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
    		self.$el.append($(QWeb.render("activity_line", {'widget':{'line':self.line},'glyphicon':'match'})));
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
                    activity_document= new local.activity_document(this,employee.employee_id,employee.name,employee.current_project,employee.activities,employee.type);
                	activity_document.appendTo(self.$el.find('div.oe_form_sheet.oe_form_sheet_width'))
        		})
        	}));
        	return $.when(defs);          
    	},
    });
    
    instance.web.client_actions.add(
            'local.action_plan', 'instance.employee_activity.action_plan');
}
