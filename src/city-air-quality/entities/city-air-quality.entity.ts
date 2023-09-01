import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm'
@Entity()
export class CityAirQuality {   
    @PrimaryGeneratedColumn()
    id: number;

    @Column()
    ts: string;

    @Column()
    aqius: number;

    @Column()
    mainus: string;

    @Column()
    aqicn: number;

    @Column()
    maincn: string;

    @Column()
    date: Date;
}
