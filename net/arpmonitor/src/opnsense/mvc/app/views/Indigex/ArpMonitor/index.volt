{{ partial("layout_partials/base_form",['fields':generalForm,'id':'frm_GeneralSettings'])}}

<script type="text/javascript">
  $( document ).ready(function) {
    mapDataToFormUI({'frm_GeneralSettings':"/api/arpmonitor/settings/get"}).done(function(data){
      // place actions to run after load, such as updating form styles
    });

    $("#saveAct").click(function() {
      saveFormToEndpoint("/api/arpmonitor/settings/set",'frm_GeneralSettings',function(){
	//action to run after a successful save, for exampel reconfigure service
	ajaxCall(url="/api/arpmonitor/service/reload", sendData={}, callback=function(data, status) {
	  //action to run after reload
	});
	ajaxCall(url="/api/arpmonitor/service/reload", sendData={}, callback=function(data,status) {
	  //action to run after reload
	});
      });
    });
  });
</script>

<div class="col-md-12">
  <button class="btn btn-primary" id="saveAct" type="button"><b>{{ lang._('Save')}}</b></button>
</div>
