import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ShellComponent } from './shell.component';
import { AppointmentsComponent } from '../appointments/appointments.component';
import { DashboardComponent } from '../dashboard/dashboard.component';
import { SettingsComponent } from '../settings/settings.component';
import { RouterModule } from '@angular/router';
import { HeaderComponent } from 'src/app/shared/ui/header/header.component';
import { SidebarComponent } from 'src/app/shared/ui/sidebar/sidebar.component';
import { MaterialModule } from 'src/app/shared/feature/material.module';
import { FormsModule } from '@angular/forms';



@NgModule({
  declarations: [
    ShellComponent,
    AppointmentsComponent,
    DashboardComponent,
    SettingsComponent,
  ],
  imports: [
    HeaderComponent,
    SidebarComponent,
    CommonModule,
    MaterialModule,
    FormsModule,
    RouterModule.forChild([
      { path: '', component: ShellComponent, children: [
        { path: '', component: DashboardComponent },
        { path: 'appointments', component: AppointmentsComponent },
        { path: 'settings', component: SettingsComponent },
      ] }
    ])
  ]
})
export class ShellModule { }
