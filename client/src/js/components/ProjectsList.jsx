import React from 'react';
import ProjectCard from './ProjectCard.jsx';


class ProjectsList extends React.Component {
    render() {
        return (
            <div className='container'>
                {this.props.projects.map((project) =>
                    <ProjectCard project={project} key={project.url}/>
                )}
            </div>
        );
    }

}

export default ProjectsList;