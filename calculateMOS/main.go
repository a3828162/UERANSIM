package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"strconv"

	"github.com/livekit/rtcscore-go/pkg/rtcmos"
)

func calculateMOS(csvFilePath string) {
	// 讀取CSV檔案
	file, err := os.Open(csvFilePath)
	if err != nil {
		log.Fatal("無法開啟CSV檔案:", err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		log.Fatal("無法讀取CSV內容:", err)
	}

	// 跳過標題行，從第二行開始處理
	if len(records) < 2 {
		log.Fatal("CSV檔案沒有資料")
	}

	// 建立stats陣列
	stats := make([]rtcmos.Stat, 0, len(records)-1)

	// 固定的VideoConfig參數
	width := int32(1920)
	height := int32(1080)
	expectFrameRate := float32(60)

	for i := 1; i < len(records); i++ {
		record := records[i]
		if len(record) < 5 {
			continue
		}

		// 解析CSV欄位
		bitrateKbps, err := strconv.ParseFloat(record[0], 32)
		if err != nil {
			log.Printf("第%d行bitrate解析失敗: %v", i+1, err)
			continue
		}
		// 將bitrate從kbps轉換成bps
		bitrate := bitrateKbps * 1000

		packetLost, err := strconv.ParseFloat(record[1], 32)
		if err != nil {
			log.Printf("第%d行packetlost解析失敗: %v", i+1, err)
			continue
		}

		jitter, err := strconv.ParseFloat(record[2], 32)
		if err != nil {
			log.Printf("第%d行jitter解析失敗: %v", i+1, err)
			continue
		}

		rtt, err := strconv.ParseFloat(record[3], 32)
		if err != nil {
			log.Printf("第%d行rtt解析失敗: %v", i+1, err)
			continue
		}

		fps, err := strconv.ParseFloat(record[4], 32)
		if err != nil {
			log.Printf("第%d行framespersecond解析失敗: %v", i+1, err)
			continue
		}

		// 轉換資料型態
		rttInt := int32(rtt)
		jitterInt := int32(jitter)
		frameRate := float32(fps)

		// 建立VideoConfig
		vConfig := rtcmos.VideoConfig{
			Codec:             "h264",
			Width:             &width,
			Height:            &height,
			FrameRate:         &frameRate,
			ExpectedFrameRate: &expectFrameRate,
		}

		// 建立Stat
		stat := rtcmos.Stat{
			PacketLoss:    float32(packetLost),
			Bitrate:       float32(bitrate),
			RoundTripTime: &rttInt,
			BufferDelay:   &jitterInt,
			VideoConfig:   &vConfig,
		}

		stats = append(stats, stat)
	}

	// fmt.Printf("成功讀取 %d 筆資料\n", len(stats))

	// 計算MOS分數
	scores := rtcmos.Score(stats)

	// 計算平均MOS分數
	var totalScore float64
	for _, sc := range scores {
		totalScore += sc.VideoScore
	}
	averageScore := totalScore / float64(len(scores))

	fmt.Printf("%.2f\n", averageScore)

	// 輸出結果
	// fmt.Println("\nMOS分數計算結果:")
	// for i, sc := range scores {
	// fmt.Printf("第%d筆 - VideoScore: %.2f\n", i+1, sc.VideoScore)
	// }

	// fmt.Printf("\n========================================\n")
	// fmt.Printf("檔案: %s\n", csvFilePath)
	// fmt.Printf("平均 MOS Score: %.2f\n", averageScore)
	// fmt.Printf("總共筆數: %d\n", len(scores))
	// fmt.Printf("========================================\n")
}

func main() {
	// 檢查命令列參數
	if len(os.Args) < 2 {
		fmt.Println("使用方法: go run main.go <相對路徑>")
		fmt.Println("範例: go run main.go random_seed44_6ue/performance_ue1.csv")
		fmt.Println("範例: go run main.go roundrobin_seed44_6ue/performance_ue5.csv")
		os.Exit(1)
	}

	// 基礎路徑
	basePath := "/home/ubuntu/UERANSIM/experiment2/"

	// 從命令列參數取得相對路徑，並組合成完整路徑
	relativePath := os.Args[1]
	fullPath := basePath + relativePath

	// 呼叫calculateMOS函數
	calculateMOS(fullPath)
}
