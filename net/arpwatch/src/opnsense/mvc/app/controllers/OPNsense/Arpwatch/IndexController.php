<?php

namespace OPNsense\Arpwatch;

class IndexController extends \OPNsense\Base\IndexController
{
    public function indexAction(): void
    {
      $this -> view -> pick('OPNsense/Arpwatch/index');
      $this -> view -> generalForm = $this -> getForm("general");
    }
}