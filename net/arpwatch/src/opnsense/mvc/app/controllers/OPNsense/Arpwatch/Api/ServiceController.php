<?php
namespace OPNsense\Arpwatch\Api;

use \OPNsense\Core\Backend;
use \OPNsense\Base\ApiMutableModelControllerBase;
class ServiceController extends ApiMutableModelControllerBase
{
  public function reloadAction(): array
  {
    $status = "failed";
    if ($this->request->isPost()) {
      $status = strtolower(trim((new Backend())->configdRun('template reload OPNsense/Arpwatch')));
    }
    return ["status" => $status];
  }

  // Could have an 'action' similar to this for each button.
  public function testAction()
  {
    if ($this -> request -> isPost()) {
      $bckresult = json_decode(trim((new Backend()) -> configdRun("arpwatch test")), true);
      if ($bckresult !== null) {
	return $bckresult;
      }
    }
    return ["message" => "unable to run config action"];
  }
}
