import { Controller, Get, Query } from '@nestjs/common';
import { CityAirQualityService } from './city-air-quality.service';

@Controller('city-air-quality')
export class CityAirQualityController {
  constructor(private readonly cityAirQualityService: CityAirQualityService) {}


  @Get()
  async getAirQuality(@Query() query){
    return await this.cityAirQualityService.getAirQuality({ longitude: query.longitude, latitude: query.latitude });
  }

  
}
