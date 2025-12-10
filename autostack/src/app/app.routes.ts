import { Routes } from '@angular/router';
import { Home } from './pages/home/home';
import { Project } from './pages/project/project';
import { Overview } from './pages/project/overview/overview';
import { Development } from './pages/project/development/development';
import { Production } from './pages/project/production/production';
import { CreateProject } from './pages/project/create-project/create-project';
import { Chat } from './pages/chat/chat';
import { ChatDetail } from './pages/chat/chat-detail/chat-detail';
import { NewChat } from './pages/chat/new-chat/new-chat';
import { LoadingChat } from './pages/chat/loading-chat/loading-chat';
import { ProjectsPage } from './pages/project/projects-page/projects-page';

export const routes: Routes = [
    {path: '', redirectTo: '/home', pathMatch: 'full'},
    {path: 'home', component: Home, data: {title: 'Dashboard'}},
    {path: 'chat', component: Chat, children: [
        {path: '', redirectTo: 'new', pathMatch: 'full'},
        {path: 'new', component: NewChat, data: {title: 'New Chat'}},
        {path: 'loading', component: LoadingChat},
        {path: ':chatid', component: ChatDetail},
    ]},
    {path: 'project/:projectId', component: Project, children: [
        {path: '', 'redirectTo': 'overview', pathMatch: 'full'},
        {path: 'overview', component: Overview},
        {path: 'production', component: Production},
        {path: 'development', component: Development},
    ]},
    {path: 'create-project', component: CreateProject},
    {path: 'project', redirectTo: '/projects', pathMatch: 'full'},
    {path: 'projects', component: ProjectsPage}
];
