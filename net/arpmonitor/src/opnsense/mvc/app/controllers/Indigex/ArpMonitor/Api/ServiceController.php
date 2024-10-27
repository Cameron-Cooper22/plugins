<?php

namespace Indigex\ArpMonitor\Api;

use OPNsense\Base\ApiMutableServiceControllerBase;
use \OPNsense\Core\Backend;
use Indigex\ArpMonitor\General;

class ServiceController extends ApiMutableServiceControllerBase
{
  protected static $internalServiceClass = '\Indigex\ArpMonitor\General';
  protected static $internalServiceTemplate = 'Indigex/ArpMonitor';
  protected static $internalServiceEnabled = 'enabled';
  protected static $internalServiceName = 'arp-monitor';

  /**
   * Here I can list all the possible functions that I may wish to call.
   * Leaving it empty for now until further isntructions from Jason/Tim.
   */

  public function reloadAction()
  {
    $status = "failed";
    if ($this -> request -> isPost()) {
      $status = strtolower(trim((new Backend()) -> configdRun('template reload Indigex/ArpMonitor')));
    }
    return ["status" => $status];
  }
}
