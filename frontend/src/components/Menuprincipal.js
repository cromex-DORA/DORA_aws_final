import React from 'react';
import { Tabs, Tab } from 'react-bootstrap';
import Milieuxaquatiques from './Milieuxaquatiques'; // Newly renamed component

const Menuprincipal = () => {
  return (
    <Tabs defaultActiveKey="milieuxaquatiques" id="main-menu" className="mb-3">
      <Tab eventKey="global" title="Global">
        <div>Content for the Global tab</div>
      </Tab>
      <Tab eventKey="milieuxaquatiques" title="Milieux Aquatiques">
        <Milieuxaquatiques />
      </Tab>
      <Tab eventKey="qualite" title="Qualité">
        <div>Content for Qualité</div>
      </Tab>
      {/* Add more tabs if needed */}
    </Tabs>
  );
};

export default Menuprincipal;
