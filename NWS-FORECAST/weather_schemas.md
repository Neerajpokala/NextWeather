# Weather API Schemas

Here are the TypeScript interfaces for the NWS Weather API responses.

## Common Types

```typescript
export interface QuantitativeValue {
  unitCode: string;
  value: number | null;
}

export interface Geometry {
  type: "Polygon" | "Point" | "MultiPolygon";
  coordinates: number[][][]; // Simplified for Polygon
}

export interface Feature {
  "@context": (string | object)[];
  id?: string;
  type: "Feature";
  geometry: Geometry;
  properties: any;
}
```

## Forecast Response Schema

Endpoint: `https://api.weather.gov/gridpoints/{office}/{gridX},{gridY}/forecast`

```typescript
export interface ForecastPeriod {
  number: number;
  name: string;
  startTime: string;
  endTime: string;
  isDaytime: boolean;
  temperature: number;
  temperatureUnit: string;
  temperatureTrend: string | null;
  probabilityOfPrecipitation: QuantitativeValue;
  windSpeed: string;
  windDirection: string;
  icon: string;
  shortForecast: string;
  detailedForecast: string;
}

export interface ForecastProperties {
  units: string;
  forecastGenerator: string;
  generatedAt: string;
  updateTime: string;
  validTimes: string;
  elevation: QuantitativeValue;
  periods: ForecastPeriod[];
}

export interface ForecastResponse extends Feature {
  properties: ForecastProperties;
}
```

## Forecast Hourly Response Schema

Endpoint: `https://api.weather.gov/gridpoints/{office}/{gridX},{gridY}/forecast/hourly`

```typescript
export interface ForecastHourlyPeriod {
  number: number;
  name: string;
  startTime: string;
  endTime: string;
  isDaytime: boolean;
  temperature: number;
  temperatureUnit: string;
  temperatureTrend: string | null;
  probabilityOfPrecipitation: QuantitativeValue;
  dewpoint: QuantitativeValue;
  relativeHumidity: QuantitativeValue;
  windSpeed: string;
  windDirection: string;
  icon: string;
  shortForecast: string;
  detailedForecast: string;
}

export interface ForecastHourlyProperties {
  units: string;
  forecastGenerator: string;
  generatedAt: string;
  updateTime: string;
  validTimes: string;
  elevation: QuantitativeValue;
  periods: ForecastHourlyPeriod[];
}

export interface ForecastHourlyResponse extends Feature {
  properties: ForecastHourlyProperties;
}
```

## Forecast Grid Data Response Schema

Endpoint: `https://api.weather.gov/gridpoints/{office}/{gridX},{gridY}`

```typescript
export interface GridDataValue {
  validTime: string;
  value: number | null;
}

export interface GridDataProperty {
  uom: string;
  values: GridDataValue[];
}

export interface ForecastGridDataProperties {
  "@id": string;
  "@type": string;
  updateTime: string;
  validTimes: string;
  elevation: QuantitativeValue;
  forecastOffice: string;
  gridId: string;
  gridX: number;
  gridY: number;
  
  // Weather Parameters
  temperature: GridDataProperty;
  dewpoint?: GridDataProperty;
  maxTemperature?: GridDataProperty;
  minTemperature?: GridDataProperty;
  relativeHumidity?: GridDataProperty;
  apparentTemperature?: GridDataProperty;
  heatIndex?: GridDataProperty;
  windChill?: GridDataProperty;
  skyCover?: GridDataProperty;
  windDirection?: GridDataProperty;
  windSpeed?: GridDataProperty;
  windGust?: GridDataProperty;
  weather?: {
      uom: string;
      values: {
          validTime: string;
          value: {
              coverage: string | null;
              weather: string | null;
              intensity: string | null;
              visibility: QuantitativeValue;
              attributes: string[];
          }[];
      }[];
  };
  hazards?: {
      values: {
          validTime: string;
          value: {
              phenomenon: string;
              significance: string;
              event_number: number | null;
          }[];
      }[];
  };
  probabilityOfPrecipitation?: GridDataProperty;
  quantitativePrecipitation?: GridDataProperty;
  iceAccumulation?: GridDataProperty;
  snowfallAmount?: GridDataProperty;
  ceilingHeight?: GridDataProperty;
  visibility?: GridDataProperty;
  transportWindSpeed?: GridDataProperty;
  transportWindDirection?: GridDataProperty;
  mixingHeight?: GridDataProperty;
  hainesIndex?: GridDataProperty;
  lightningActivityLevel?: GridDataProperty;
  twentyFootWindSpeed?: GridDataProperty;
  twentyFootWindDirection?: GridDataProperty;
  waveHeight?: GridDataProperty;
  wavePeriod?: GridDataProperty;
  waveDirection?: GridDataProperty;
  primarySwellHeight?: GridDataProperty;
  primarySwellDirection?: GridDataProperty;
  secondarySwellHeight?: GridDataProperty;
  secondarySwellDirection?: GridDataProperty;
  wavePeriod2?: GridDataProperty;
  windWaveHeight?: GridDataProperty;
  dispersionIndex?: GridDataProperty;
  pressure?: GridDataProperty;
  probabilityOfTropicalCycloneWinds?: GridDataProperty;
  probabilityOfHurricaneWinds?: GridDataProperty;
  potentialOf15mphWinds?: GridDataProperty;
  potentialOf30mphWinds?: GridDataProperty;
  potentialOf45mphWinds?: GridDataProperty;
  potentialOf60mphWinds?: GridDataProperty;
  grasslandFireDangerIndex?: GridDataProperty;
  probabilityOfThunder?: GridDataProperty;
  davisStabilityIndex?: GridDataProperty;
  atmosphericDispersionIndex?: GridDataProperty;
  lowVisibilityOccurrenceRiskIndex?: GridDataProperty;
  stability?: GridDataProperty;
  redFlagThreatIndex?: GridDataProperty;
}

export interface ForecastGridDataResponse extends Feature {
  properties: ForecastGridDataProperties;
}
```
