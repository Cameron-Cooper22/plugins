<?php


namespace OPNsense\Arpmonitor\Api;

use OPNsense\Base\ApiControllerBase;
use OPNsense\Core\Backend;

class DaemonController extends ApiControllerBase
{
  public function startAction()
  {
    $message = " ";
    if ($this->request->isPost()) {
      $message = strtolower(trim((new Backend()) -> configdRun('arpmonitor start_daemon')));
    }
    return ["message" => "Daemon started"];
  }
  public function arplogAction()
  {
    $backend = new Backend();
    $response = $backend -> configdRun('arpmonitor arplog');
    return array("response" => $response)
  }
}
