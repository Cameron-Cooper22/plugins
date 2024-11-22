<script type="text/javascript">
  $( document ).ready(function() {
    mapDataToFormUI({'frm_GeneralSettings':"/api/arpwatch/settings/get"}).done(function(data) {
      // actions to run following load
    });

    $("#saveAct").click(function() {
      saveFormToEndpoint("api/arpwatch/settings/set",'frm_GeneralSettings',function() {
	ajaxCall(url="/api/arpwatch/service/reload", sendData={}, callback = function(data, status) {
	  
	});
      });
    });
    $("#testAct").SimpleActionButton({
      onAction: function(data) {
	$("#responseMsg").html(data['message']);
      }
    });
    $("#startAct").SimpleActionButton({
      onAction: function(data) {
	$("#responseMsg").html(data['message']);
      }
    });
  });
</script>

<div class="col-md-12">
    <button class="btn btn-primary"  id="saveAct" type="button"><b>{{ lang._('Save') }}</b></button>
</div>

<div class="alert alert-info hidden" role="alert" id="responseMsg">
    <button class="btn btn-primary" id="testAct" data-endpoint="/api/arpwatch/service/test" data-label="{{ lang._('Test') }}"></button>
    <button class="btn btn-primary" id="startAct" data-endpoint="/api/arpwatch/service/start_daemon" data-label="{{ lang._('Start Daemon') }}"></button>
</div>
