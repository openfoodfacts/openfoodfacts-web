import AppKit

let inputPath = "html/images/misc/mobileapp/new_openfoodfacts_app_en_light_3_screenshots.png"
let outputPath = "html/images/producers/official-app-screenshot.png"

guard let image = NSImage(contentsOfFile: inputPath) else {
    print("Cannot read image")
    exit(1)
}

guard let rep = image.representations.first as? NSBitmapImageRep else {
    print("Cannot get rep")
    exit(1)
}

print("Width: \(rep.pixelsWide), Height: \(rep.pixelsHigh)")

// In NSImage coordinate system, Y=0 is at bottom unless flipped.
// Let's find left phone bbox:
// Phone is roughly in left third: x between 100 and 650.
var minX = rep.pixelsWide, maxX = 0, minY = rep.pixelsHigh, maxY = 0

for y in 0..<rep.pixelsHigh {
    for x in 100..<650 {
        if let color = rep.colorAt(x: x, y: y) {
            // Check if phone chassis / screen pixel (not white/cream background)
            // Background is creamy: r > 0.95, g > 0.93, b > 0.88 or alpha == 0
            let r = color.redComponent
            let g = color.greenComponent
            let b = color.blueComponent
            let a = color.alphaComponent
            
            let isBg = (a < 0.1) || (r > 0.94 && g > 0.93 && b > 0.85) || (r > 0.98 && g > 0.98 && b > 0.98)
            if !isBg {
                if x < minX { minX = x }
                if x > maxX { maxX = x }
                if y < minY { minY = y }
                if y > maxY { maxY = y }
            }
        }
    }
}

print("Detected Phone Bounds: x: \(minX)...\(maxX), y: \(minY)...\(maxY)")
let padding = 10
let cropX = max(0, minX - padding)
let cropY = max(0, minY - padding)
let cropW = min(rep.pixelsWide - cropX, (maxX - minX + 1) + 2 * padding)
let cropH = min(rep.pixelsHigh - cropY, (maxY - minY + 1) + 2 * padding)

let cropRect = CGRect(x: cropX, y: cropY, width: cropW, height: cropH)
print("Crop Rect: \(cropRect)")

guard let cgImage = rep.cgImage?.cropping(to: cropRect) else {
    print("Cropping failed")
    exit(1)
}

let outRep = NSBitmapImageRep(cgImage: cgImage)
guard let pngData = outRep.representation(using: .png, properties: [:]) else {
    print("PNG encoding failed")
    exit(1)
}

try pngData.write(to: URL(fileURLWithPath: outputPath))
print("Successfully written to \(outputPath) with size \(cropW)x\(cropH)")
