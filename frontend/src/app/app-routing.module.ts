import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: '', loadChildren: () => import('./landing-page/shell/shell.module').then(m => m.ShellModule) },
  { path: 'login', loadChildren: () => import('./login-page/shell/shell.module').then(m => m.ShellModule) },
  { path: 'register', loadChildren: () => import('./register-page/shell/shell.module').then(m => m.ShellModule) },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }