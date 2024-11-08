<?php

namespace OPNsense\Arpwatch\Api;

use OPNsense\Base\ApiMutableServiceControllerBase;
use OPNsense\Core\Backend;
use OPNsense\Arowatch\General;

class ServiceController extends ApiMutableServiceControllerBase
{
    protected static $internalServiceClass = '\OPNsense\Arpwatch\General';
    protected static $internalServiceTemplate = 'OPNsense/Arpwatch';
    protected static $internalServiceEnabled = 'enabled';
    protected static $internalServiceName = 'arpwatch';

    public function queryArp()
    {
        $backend = new Backend();
        $response = $backend->configdRun("arpwatch gettable");
        return array("response" => $response);
    }

    public function resetdbAction()
    {
        $backend = new Backend();
        $response = $backend->configdRun("vnstat resetdb");
        return array("response" => $response);
    }
}
