#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
binmode(STDOUT, ":utf8");

# Script to detect repeated text patterns in translation files
# This helps catch issues where Crowdin or translators accidentally duplicate text

my $errors_found = 0;
my $files_checked = 0;

# Check for text repetitions in HTML files
sub check_repetitions {
    my ($file) = @_;
    
    open(my $fh, '<:utf8', $file) or return;
    my @lines = <$fh>;
    close($fh);
    
    my $content = join('', @lines);
    
    # Remove HTML comments
    $content =~ s/<!--.*?-->//gs;
    
    # Remove style blocks (CSS is expected to have repeated patterns)
    $content =~ s/<style[^>]*>.*?<\/style>//gsi;
    
    my @issues;
    
    # Pattern 1: Same substantial text appearing 2+ times consecutively with space/newline between
    # Looking for patterns like "Text Text" or "Text Text Text"
    my $min_len = 20;
    while ($content =~ /([^\n<]{$min_len,}?)\s+\1/g) {
        my $match = $1;
        
        # Skip pure HTML tags and structural elements
        next if $match =~ /^<[^>]+>$/;
        next if $match =~ /^[\s\n\r\t<>\/]+$/;
        next if $match =~ /^(div|p|span|strong|em|li|ul|ol)$/i;
        next if $match =~ /^[a-z0-9_-]+$/i;  # CSS classes, IDs, technical strings
        next if $match =~ /^["\'\(\)\[\]{}]+$/;  # Quotes and brackets
        
        # Skip CSS-like patterns (properties, values, selectors)
        next if $match =~ /^\s*(box-shadow|animation|transform|transition|rgba|scale|translate|rotate|skew|matrix)[\s:;(]/i;
        next if $match =~ /^\s*\.(mod-|btn-|nav-|header-|footer-|sidebar-)/i;  # CSS class selectors
        next if $match =~ /^\s*and\s*\(\s*(min-|max-)(width|height)/i;  # Media queries
        next if $match =~ /^\s*[\d.]+\s*(px|em|rem|%|vh|vw|s|ms)\s*[,;)]/;  # CSS values
        next if $match =~ /^\s*#[a-fA-F0-9]{3,8}\s*[;,)]/;  # Hex colors
        next if $match =~ /^\s*null\s*,/;  # JavaScript null patterns
        
        my $preview = $match;
        $preview =~ s/\s+/ /g;
        $preview = substr($preview, 0, 70) . "..." if length($preview) > 70;
        push @issues, $preview;
    }
    
    if (@issues) {
        print "\n❌ REPETITION in $file:\n";
        foreach my $issue (@issues) {
            print "   → \"$issue\"\n";
        }
        return scalar(@issues);
    }
    
    return 0;
}

# Process files
my @files;
if (@ARGV) {
    @files = @ARGV;
} else {
    # Find all HTML files in lang/ directory
    @files = `find lang/ -name '*.html' -type f 2>/dev/null`;
    chomp(@files);
}

foreach my $file (@files) {
    next unless -f $file && $file =~ /\.html$/;
    $files_checked++;
    $errors_found += check_repetitions($file);
}

print "\n" . "=" x 70 . "\n";
print "📊 Summary: Checked $files_checked files\n";

if ($errors_found > 0) {
    print "❌ Found $errors_found repetition error(s)\n";
    print "=" x 70 . "\n";
    print "\n💡 Tip: These errors often occur when text is accidentally duplicated\n";
    print "   during translation. Please review and remove the duplicate text.\n\n";
    exit 1;
} else {
    print "✅ No repetition errors found!\n";
    print "=" x 70 . "\n";
    exit 0;
}
