import { Controller, Get, Post, Body, Patch, Param, Delete, Query } from '@nestjs/common';
import { CityAirQualityService } from './city-air-quality.service';
import { CreateCityAirQualityDto } from './dto/create-city-air-quality.dto';
import { UpdateCityAirQualityDto } from './dto/update-city-air-quality.dto';

@Controller('city-air-quality')
export class CityAirQualityController {
  constructor(private readonly cityAirQualityService: CityAirQualityService) {}


  @Get()
  async getAirQuality(@Query() query){
    return await this.cityAirQualityService.getAirQuality({ longitude: query.longitude, latitude: query.latitude });
  }

  
}
