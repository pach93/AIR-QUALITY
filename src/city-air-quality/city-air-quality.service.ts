import { HttpException, HttpStatus, Injectable, UnsupportedMediaTypeException } from '@nestjs/common';
import { CreateCityAirQualityDto } from './dto/create-city-air-quality.dto';
import { UpdateCityAirQualityDto } from './dto/update-city-air-quality.dto';
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
        error: 'unsopported longitude type',
      }, HttpStatus.FORBIDDEN, {
        cause: error
      });
    }

    if(!cleaned_latitude || cleaned_latitude < -90 || cleaned_latitude > 90){
      throw new HttpException({
        status: HttpStatus.FORBIDDEN,
        error: 'unsopported latitude type',
      }, HttpStatus.FORBIDDEN, {
        cause: error
      });
    }
    console.log(cleaned_longitude)
    const datas = (await axios.get(`http://api.airvisual.com/v2/nearest_city?lat=${cleaned_latitude}&lon=${cleaned_longitude}&key=c860c685-96a2-40ae-9d2a-10563eb4a901`)).data
    // await console.log(data)
    const results = {
      "Result":{
        "Pollution": datas.data.current.pollution
      }
    }
    return results
  }

  @Cron('* * * * *')
  async handleCron() {
    const airQuality = new CityAirQuality()
    const datas = (await axios.get(`http://api.airvisual.com/v2/nearest_city?lat=48.856613&lon=2.352222&key=c860c685-96a2-40ae-9d2a-10563eb4a901`)).data
    // await console.log(data)
    const results = datas.data.current.pollution

    airQuality.aqicn = results.aqicn
    airQuality.aqius = results.aqius
    airQuality.maincn = results.maincn
    airQuality.mainus = results.mainus
    airQuality.ts = results.ts

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
      // console.log('taskService#error@data', e ? e.message.substring(0, 12) : '');
    }


    console.log(results);
  }
}
