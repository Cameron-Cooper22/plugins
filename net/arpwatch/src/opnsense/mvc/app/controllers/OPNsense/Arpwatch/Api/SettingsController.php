<?php

namespace OPNsense\Arpwatch\Api;

use OPNsense\Base\ApiMutableModelControllerBase;

class SettingsController extends ApiMutableModelControllerBase
{
    protected static $internalModelClass = 'OPNsense\Arpwatch\Arpwatch';
    protected static $internalModelName = 'arpwatch';
}
