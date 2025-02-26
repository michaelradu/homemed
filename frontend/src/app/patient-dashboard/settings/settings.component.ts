import { Component } from '@angular/core';
import { Store } from '@ngrx/store';
import { filter, Observable, switchMap } from 'rxjs';
import { FilesService } from 'src/app/shared/data-access/files.service';
import { PatientsService } from 'src/app/shared/data-access/patients.service';
import { getUser } from 'src/app/store/user/user.selector';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss']
})
export class SettingsComponent {
  constructor(private store: Store, private patientsService: PatientsService, private filesService: FilesService) { }
  
  avatarId! : number

  user$ : Observable<any> = this.store.select(getUser).pipe(
    filter((user: any) => user != null)
  )

  patient$ : Observable<any> = this.user$.pipe(
    switchMap((user: any) => this.patientsService.getPatient(user.uid))
  )

  onUpdatePatient(patient : any) {
    if (this.avatarId) patient.avatarId = this.avatarId
    this.patientsService.updatePatient(patient).subscribe()
  }

  onChangeAvatar(e : any) {
    this.filesService.addFile(e.target.files[0]).subscribe((res: any) => this.avatarId = res)
  }
}
