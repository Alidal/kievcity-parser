import App from './components/App.jsx'
import ReactDOM from 'react-dom';
import React from 'react';

var ws = new WebSocket('ws://' + window.location.host + '/ws');
ws.onmessage = function(event) {
    let projects = JSON.parse(event.data)

    ReactDOM.render(
      <App projects={projects}/>,
      document.getElementById('root')
    );

    console.log("Got fresh data")
};