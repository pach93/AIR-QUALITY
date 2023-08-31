import { Test, TestingModule } from '@nestjs/testing';
import { CityAirQualityController } from './city-air-quality.controller';
import { CityAirQualityService } from './city-air-quality.service';

describe('CityAirQualityController', () => {
  let controller: CityAirQualityController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [CityAirQualityController],
      providers: [CityAirQualityService],
    }).compile();

    controller = module.get<CityAirQualityController>(CityAirQualityController);
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });
});
