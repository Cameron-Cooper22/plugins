<?php

namespace OPNsense\Arpmonitor\Api;

use OPNsense\Base\ApiMutableModelControllerBase;

class SettingsController extends ApiMutableModelControllerBase
{
    protected static $internalModelClass = 'OPNsense\Arpmonitor\Arpmonitor';
    protected static $internalModelName = 'arpmonitor';
}
