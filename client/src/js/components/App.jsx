import React from 'react';
import ProjectsList from './ProjectsList.jsx';

class App extends React.Component {
    render() {
        return (
            <ProjectsList projects={this.props.projects}/>
        )
    }
}

export default App;