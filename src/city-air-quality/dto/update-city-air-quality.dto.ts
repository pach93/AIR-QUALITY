import { PartialType } from '@nestjs/mapped-types';
import { CreateCityAirQualityDto } from './create-city-air-quality.dto';

export class UpdateCityAirQualityDto extends PartialType(CreateCityAirQualityDto) {}
