import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { CityAirQualityModule } from './city-air-quality/city-air-quality.module';

@Module({
  imports: [CityAirQualityModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
