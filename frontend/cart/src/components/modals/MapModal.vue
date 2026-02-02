<template>
  <div class="market-map">

    <!-- 입구 -->
    <div class="gate entrance">입구</div>

    <!-- A 존 -->
    <ZoneBox class="a01" :zone="zoneMap['A-01']" :active="highlightZone==='A-01'" />
    <ZoneBox class="a10" :zone="zoneMap['A-10']" :active="highlightZone==='A-10'" />
    <ZoneBox class="a20" :zone="zoneMap['A-20']" :active="highlightZone==='A-20'" />
    <ZoneBox class="a30" :zone="zoneMap['A-30']" :active="highlightZone==='A-30'" />

    <!-- C 존 -->
    <ZoneBox class="c03" :zone="zoneMap['C-03']" :active="highlightZone==='C-03'" />
    <ZoneBox class="c10" :zone="zoneMap['C-10']" :active="highlightZone==='C-10'" />

    <!-- B 존 -->
    <ZoneBox class="b02" :zone="zoneMap['B-02']" :active="highlightZone==='B-02'" />
    <ZoneBox class="b10" :zone="zoneMap['B-10']" :active="highlightZone==='B-10'" />
    <ZoneBox class="b20" :zone="zoneMap['B-20']" :active="highlightZone==='B-20'" />

    <!-- D / E -->
    <ZoneBox class="d04" :zone="zoneMap['D-04']" :active="highlightZone==='D-04'" />
    <ZoneBox class="e05" :zone="zoneMap['E-05']" :active="highlightZone==='E-05'" />

    <!-- 출구 -->
    <div class="gate exit">출구</div>

  </div>
</template>


<script setup>
import ZoneBox from '../ZoneBox.vue'

defineProps({
  highlightZone: String
})

const zoneMap = {
  'A-01': { code: 'A-01', name: '채소/과일' },
  'A-10': { code: 'A-10', name: '통조림' },
  'A-20': { code: 'A-20', name: '소스류' },
  'A-30': { code: 'A-30', name: '면류' },

  'B-02': { code: 'B-02', name: '정육/계란' },
  'B-10': { code: 'B-10', name: '즉석식품' },
  'B-20': { code: 'B-20', name: '잼/스프레드' },

  'C-03': { code: 'C-03', name: '수산/해산물' },
  'C-10': { code: 'C-10', name: '음료' },

  'D-04': { code: 'D-04', name: '가공/유제품' },
  'E-05': { code: 'E-05', name: '양념/오일' }
}
</script>

<style scoped>
.market-map {
  display: grid;
  grid-template-columns: 0.6fr 1.6fr 1fr 1fr 1fr 1fr;
  grid-template-rows: auto auto auto auto;
  gap: 10px;
  margin-top: 16px;

  grid-template-areas:
    "enter a01 a01 a01 c03 c03"
    ".     a10 a20 a30 c10 c10"
    ".     b02 b02 b02 b10 b10"
    ".     b20 b20 d04 e05 exit";
}

/* 입·출구 */
.entrance { grid-area: enter; }
.exit     { grid-area: exit; }

/* A 존 */
.a01 { grid-area: a01; }
.a10 { grid-area: a10; }
.a20 { grid-area: a20; }
.a30 { grid-area: a30; }

/* B 존 */
.b02 { grid-area: b02; }
.b10 { grid-area: b10; }
.b20 { grid-area: b20; }

/* 사이드 */
.c03 { grid-area: c03; }
.c10 { grid-area: c10; }
.d04 { grid-area: d04; }
.e05 { grid-area: e05; }

/* 입·출구 스타일 */
.gate {
  border: 2px dashed #94a3b8;
  border-radius: 14px;
  background: #f1f5f9;
  font-weight: bold;
  font-size: 14px;

  display: flex;
  align-items: center;
  justify-content: center;
}

</style>
