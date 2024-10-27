<?php

namespace Indigex\ArpMonitor;

class IndexController extends \OPNsense\Base\IndexController
{
  public function indexAction()
  {
    // View to be shown to users from app/views/Indigex/ArpMonitor/index.volt
    $this -> view -> pick('Indigex/ArpMonitor/general');

    $this -> view -> generalForm = $this -> getForm("general");
  }
}
