<script type="text/javascript">
    $( document ).ready(function() {
        mapDataToFormUI({'frm_GeneralSettings':"/api/arpmonitor/settings/get"}).done(function(data){
            // place actions to run after load, for example update form styles.
        });

        // link save button to API set action
        $("#saveAct").click(function(){
            saveFormToEndpoint("/api/arpmonitor/settings/set",'frm_GeneralSettings',function(){
                // action to run after successful save, for example reconfigure service.
                ajaxCall(url="/api/arpmonitor/service/reload", sendData={},callback=function(data,status) {
                    // action to run after reload
                });
            });
        });
	$("#testAct").SimpleActionButton({
	    onAction: function(data) {
		$("#responseMsg").removeClass("hidden").html(data['message']);
	    }
	});
    });
</script>


<div class="alert alert-info hidden" role="alert" id="responseMsg">

</div>

<div  class="col-md-12">
    {{ partial("layout_partials/base_form",['fields':generalForm,'id':'frm_GeneralSettings'])}}
</div>

<div class="col-md-12">
    <button class="btn btn-primary"  id="saveAct" type="button"><b>{{ lang._('Save') }}</b></button>
    <button class="btn btn-primary" id="testAct" data-endpoint="/api/arpmonitor/service/test" data-label="{{ lang._('Test') }}"></button>
</div>
