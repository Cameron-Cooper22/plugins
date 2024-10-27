<?php

namespace Indigex\ArpMonitor\Api;

use \OPNsense\Base\ApiMutableModelControllerBase;

/**
 * This class contains any settings implementations that I may add in the future.
 */
class SettingsController extends ApiMutableModelControllerBase
{
  protected static $internalModelClass = '\Indigex\ArpMonitor\ArpMonitor';
  protected static $internalModelName = 'arpmonitor';
}
