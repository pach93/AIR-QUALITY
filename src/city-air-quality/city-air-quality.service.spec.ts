import { Test, TestingModule } from '@nestjs/testing';
import { CityAirQualityService } from './city-air-quality.service';

describe('CityAirQualityService', () => {
  let service: CityAirQualityService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [CityAirQualityService],
    }).compile();

    service = module.get<CityAirQualityService>(CityAirQualityService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });
});
