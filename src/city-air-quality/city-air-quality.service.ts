import { HttpException, HttpStatus, Injectable, UnsupportedMediaTypeException } from '@nestjs/common';

import axios from 'axios';
import { error } from 'console';
import { Cron } from '@nestjs/schedule';
import { CityAirQuality } from './entities/city-air-quality.entity';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';


@Injectable()
export class CityAirQualityService {
  constructor(
    @InjectRepository(CityAirQuality)
    private readonly userRepository: Repository<CityAirQuality>,
    
  ) {}
  remove(id: number) {
    return `This action removes a #${id} cityAirQuality`;
  }

  async getAirQuality({longitude, latitude}){
    const cleaned_longitude = parseFloat(longitude)
    const cleaned_latitude = parseFloat(latitude)

    if(!cleaned_longitude || cleaned_longitude < -180 || cleaned_longitude > 180){
      throw new HttpException({
        status: HttpStatus.FORBIDDEN,
        error: 'longitude should be between -180 and 180',
      }, HttpStatus.FORBIDDEN, {
        cause: error
      });
    }

    if(!cleaned_latitude || cleaned_latitude < -90 || cleaned_latitude > 90){
      throw new HttpException({
        status: HttpStatus.FORBIDDEN,
        error: 'latitude should be between -90 and 90',
      }, HttpStatus.FORBIDDEN, {
        cause: error
      });
    }
    // console.log(cleaned_longitude)
    try {
      const datas = (await axios.get(`http://api.airvisual.com/v2/nearest_city?lat=${cleaned_latitude}&lon=${cleaned_longitude}&key=c860c685-96a2-40ae-9d2a-10563eb4a901`)).data
      await console.log(datas.status)
      const results = {
        "Result":{
          "Pollution": datas.data.current.pollution
        }
      }
      return results
    } catch (e) {
      console.log('airService#error@data', e ? e.message : '');
      throw new HttpException({
        status: HttpStatus.BAD_REQUEST,
        error: 'unsopported longitude or latitude values',
      }, HttpStatus.BAD_REQUEST, {
        cause: error
      });
      
    }
    
  }

  @Cron('* * * * *')
  async handleCron() {
    const airQuality = new CityAirQuality()
    try {
      const datas = (await axios.get(`http://api.airvisual.com/v2/nearest_city?lat=48.856613&lon=2.352222&key=c860c685-96a2-40ae-9d2a-10563eb4a901`)).data
      const results = datas.data.current.pollution
      airQuality.aqicn = results.aqicn
      airQuality.aqius = results.aqius
      airQuality.maincn = results.maincn
      airQuality.mainus = results.mainus
      airQuality.ts = results.ts
      console.log(results);
    } catch (e) {
      console.log('airService#error@data', e ? e.message.substring(0, 12) : '');
    }
    
    // await console.log(data)
    

    

    const currentdate = new Date(); 
    const datetime = currentdate.getDate() + "/"
                    + (currentdate.getMonth()+1)  + "/" 
                    + currentdate.getFullYear() + " @ "  
                    + currentdate.getHours() + ":"  
                    + currentdate.getMinutes() + ":" 
                    + currentdate.getSeconds();
    
    airQuality.date = new Date(datetime)
    try {
      await this.userRepository.save(airQuality);
    } catch (e) {
      console.log('airService#error@data', e ? e.message : '');
    }


    
  }
}
