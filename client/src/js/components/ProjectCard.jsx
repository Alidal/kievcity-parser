import React from 'react';
import styles from '../../css/app.css'

class ProjectCardHeader extends React.Component {
    render() {
        return (
            <div className="title">
                <a href={this.props.url}>
                    {this.props.title}
                </a>
            </div>
        );
    }
}

class ProjectCardBody extends React.Component {
    // Formatting for big numbers
    numberWithCommas(x) {
        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }


    render() {
        return (
            <div className='card-content black-text fixed-height-description'>
                <p>{this.props.description}</p>
                <hr/>
                <p><b>Бюджет</b>: {this.numberWithCommas(this.props.budget)} грн</p>
                <p><b>Район</b>: {this.props.district} </p>
                <p><b>Автор</b>: {this.props.author} </p>
            </div>
        );
    }
}

class ProjectCardFooter extends React.Component {
    render() {
        return (
            <div className='card-action'>
                <a className='blue-text darken-4-text' href={this.props.url}>
                    Голосовать ({this.props.votes})
                </a>
            </div>
        );
    }
}

class ProjectCard extends React.Component {
    render() {
        const project = this.props.project
        let classes = 'card '
        if (project.is_kpi) {
            classes += 'green lighten-4'
        } else if (project.is_top) {
            classes += 'green lighten-5'
        } else {
            classes += 'red lighten-5 '
        }
        return (
            <div className='col-sm-12 col-md-4'>
                <div className={classes}>
                    <ProjectCardHeader title={project.title}
                                       url={project.url} />
                    <hr/>
                    <ProjectCardBody description={project.description}
                                     budget={project.budget}
                                     district={project.district}
                                     author={project.author} />
                    <ProjectCardFooter votes={project.votes}
                                       url={project.url} />
                </div>
            </div>
        );
    }

}

export default ProjectCard;
