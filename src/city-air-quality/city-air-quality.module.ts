import { Module } from '@nestjs/common';
import { CityAirQualityService } from './city-air-quality.service';
import { CityAirQualityController } from './city-air-quality.controller';
import { TypeOrmModule } from '@nestjs/typeorm';
import { CityAirQuality } from './entities/city-air-quality.entity';

@Module({
  imports: [TypeOrmModule.forFeature([CityAirQuality])],
  controllers: [CityAirQualityController],
  providers: [CityAirQualityService],
})
export class CityAirQualityModule {}
