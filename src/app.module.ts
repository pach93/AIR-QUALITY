import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { CityAirQualityModule } from './city-air-quality/city-air-quality.module';
import { ScheduleModule } from '@nestjs/schedule';
import { TypeOrmModule } from '@nestjs/typeorm';
import { CityAirQuality } from './city-air-quality/entities/city-air-quality.entity';

@Module({
  imports: [
    CityAirQualityModule,
    ScheduleModule.forRoot(),
    TypeOrmModule.forRoot({
      type: "mysql",
      host: "localhost",
      port: 3306,
      username: "root",
      password: "",
      database: "air-quality",
      entities: [CityAirQuality],
      synchronize: true
    })],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
