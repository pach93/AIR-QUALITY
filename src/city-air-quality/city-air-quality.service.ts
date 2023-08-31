import { HttpException, HttpStatus, Injectable, UnsupportedMediaTypeException } from '@nestjs/common';
import { CreateCityAirQualityDto } from './dto/create-city-air-quality.dto';
import { UpdateCityAirQualityDto } from './dto/update-city-air-quality.dto';
import axios from 'axios';
import { ExceptionsHandler } from '@nestjs/core/exceptions/exceptions-handler';
import { error } from 'console';

@Injectable()
export class CityAirQualityService {

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
}
