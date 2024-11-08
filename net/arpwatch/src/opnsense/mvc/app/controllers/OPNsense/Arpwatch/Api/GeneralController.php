<?php

namespace OPNsense\Vnstat\Api;

use OPNsense\Base\ApiMutableModelControllerBase;

class GeneralController extends ApiMutableModelControllerBase
{
    protected static $internalModelClass = '\OPNsense\Arpwatch\General';
    protected static $internalModelName = 'general';
}
