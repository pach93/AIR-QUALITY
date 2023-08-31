import { Module } from '@nestjs/common';
import { CityAirQualityService } from './city-air-quality.service';
import { CityAirQualityController } from './city-air-quality.controller';

@Module({
  controllers: [CityAirQualityController],
  providers: [CityAirQualityService],
})
export class CityAirQualityModule {}
