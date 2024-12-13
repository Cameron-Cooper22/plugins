{#

OPNsense® is Copyright © 2014 – 2015 by Deciso B.V.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1.  Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

2.  Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

#}
<!-- Navigation bar -->
<ul class="nav nav-tabs" data-tabs="tabs" id="maintabs">
    <li class="active"><a data-toggle="tab" href="#general">{{ lang._('General') }}</a></li>
    <li><a data-toggle="" href="#arplog">{{ lang._('Arpwatch Log') }}</a></li>
    <li><a data-toggle="tab" href="#arpdat">{{ lang._('arp.dat') }}</a></li>
</ul>
<div class="tab-content content-box tab-content">
    <div id="general" class="tab-pane fade in active">
        <div class="content-box" style="padding-bottom: 1.5em;">
            {{ partial("layout_partials/base_form",['fields':generalForm,'id':'frm_general_settings'])}}
            <div class="col-md-12">
                <hr />
                <button class="btn btn-primary" id="saveAct" type="button"><b>{{ lang._('Save') }}</b> <i id="saveAct_progress"></i></button>
            </div>
        </div>
    </div>
    <div id="arplog" class="tab-pane fade in">
      <pre id="listarplog"></pre>
    </div>
    <div id="arpdat" class="tab-pane fade in">
      <pre id="listarpdat"></pre>
    </div>
    <div id="monthly" class="tab-pane fade in">
      <pre id="listmonthly"></pre>
    </div>
    <div id="yearly" class="tab-pane fade in">
      <pre id="listyearly"></pre>
    </div>
</div>
<script>

function update_arpdat() {
  ajaxCall(url="/api/arpmonitor/daemon/arplog", sendData={}, callback=function(data,status) {
        $("#listarplog").text(data['response']);
    });
}
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

	$("#logAct").click(function(){
	  ajaxGet('/api/arpmonitor/daemon/log', sendData={}, callback=function(data,status) {
	    // action to run after pulling log file
	  });
	});

        // use a SimpleActionButton() to call /api/arpmonitor/service/testthisshit
        $("#testAct").SimpleActionButton({
            onAction: function(data) {
                $("#responseMsg").removeClass("hidden").html(data['message']);
            }
        });
	
	$("#startAct").SimpleActionButton({
	    onAction: function(data) {
		$("#responseMsg").removeClass("hidden").html(data['message']);
	    }
	});
    });
</script>

<div class="alert alert-info hidden" role="alert" id="responseMsg">

</div>

