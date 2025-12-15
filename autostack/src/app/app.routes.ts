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
import { ProjectSettings } from './pages/project/settings/settings';
import { ComponentProjectSettings } from './pages/project/settings/component-project-settings/component-project-settings';
import { GeneralProjectSettings } from './pages/project/settings/general-project-settings/general-project-settings';
import { VersionControlProjectSettings } from './pages/project/settings/version-control-project-settings/version-control-project-settings';
import { Operations } from './pages/operations/operations';
import { OperationDetail } from './pages/operations/operation-detail/operation-detail';

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
        {path: 'settings', component: ProjectSettings, children: [
            {path: '', redirectTo: 'general', pathMatch: 'full'},
            {path: 'general', component: GeneralProjectSettings},
            {path: 'components', component: ComponentProjectSettings},
            {path: 'version-control', component: VersionControlProjectSettings},
        ]},
    ]},
    {path: 'create-project', component: CreateProject},
    {path: 'project', redirectTo: '/projects', pathMatch: 'full'},
    {path: 'projects', component: ProjectsPage, data: {title: 'Projects'}},
    {path: 'operations', component: Operations, children: [
        {path: ':operationsId', component: OperationDetail}
    ]}
];
