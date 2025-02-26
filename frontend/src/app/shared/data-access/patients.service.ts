import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { tap } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class PatientsService {

  constructor(private http: HttpClient) { }

  readonly apiURL = environment.apiURL + 'patients/'

  getPatient(uid : any) {
    return this.http.get(`${this.apiURL}get/${uid}/`)
  }

  updatePatient(patient : any) {
    return this.http.put(`${this.apiURL}update/${patient.uid}/`, patient)
  }

  transferPatient(data : any) {
    return this.http.post(`${this.apiURL}transfer/`, data)
  }
}
