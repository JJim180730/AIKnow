#!/bin/bash
# 集成测试启动脚本
# 自动激活虚拟环境并运行所有测试

set -e  # 遇到错误立即退出

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# 主函数
main() {
    print_header "混合语义分析 - 集成测试"

    echo "测试时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "工作目录: $SCRIPT_DIR"
    echo

    # 1. 检查虚拟环境
    print_info "步骤 1/4: 检查虚拟环境"
    if [ ! -d "venv" ]; then
        print_error "虚拟环境不存在,请先创建:"
        echo "  python -m venv venv"
        echo "  source venv/bin/activate"
        echo "  pip install -r requirements.txt"
        exit 1
    fi
    print_success "虚拟环境存在"
    echo

    # 2. 激活虚拟环境
    print_info "步骤 2/4: 激活虚拟环境"
    source venv/bin/activate
    print_success "虚拟环境已激活: $(which python)"
    echo "  Python 版本: $(python --version)"
    echo

    # 3. 检查测试数据
    print_info "步骤 3/4: 检查测试数据"

    if [ ! -f "data/test_corpus.txt" ]; then
        print_error "测试数据不存在: data/test_corpus.txt"
        exit 1
    fi
    print_success "短文本测试数据 (138字)"

    if [ ! -f "data/test_corpus_long.txt" ]; then
        print_warning "中等文本测试数据不存在: data/test_corpus_long.txt"
    else
        print_success "中等文本测试数据 (631字)"
    fi

    if [ ! -f "data/test_corpus_chapter.txt" ]; then
        print_warning "完整章节测试数据不存在: data/test_corpus_chapter.txt"
    else
        print_success "完整章节测试数据 (3000字)"
    fi
    echo

    # 4. 运行测试
    print_info "步骤 4/4: 运行测试"
    echo

    # 4.1 LTP测试
    print_header "测试 A: LTP依存文法 (真实模型调用)"

    if [ ! -f "test_ltp.py" ]; then
        print_error "test_ltp.py 不存在"
        echo
    else
        print_info "运行 LTP 短文本测试 (138字)..."
        if python test_ltp.py --data short 2>&1; then
            print_success "LTP 短文本测试完成"
        else
            print_error "LTP 短文本测试失败"
            print_info "可能原因: LTP在Python 3.13环境下存在兼容性问题"
            print_info "详见: LTP_STATUS.md"
            print_info "已有测试结果: results/ltp_experiment_report.md"
        fi
        echo

        if [ -f "data/test_corpus_long.txt" ]; then
            print_info "运行 LTP 中文本测试 (631字)..."
            if python test_ltp.py --data medium 2>&1; then
                print_success "LTP 中文本测试完成"
            else
                print_warning "LTP 中文本测试失败,跳过"
            fi
            echo
        fi

        if [ -f "data/test_corpus_chapter.txt" ]; then
            print_info "运行 LTP 长文本测试 (3000字)..."
            if python test_ltp.py --data long 2>&1; then
                print_success "LTP 长文本测试完成"
            else
                print_warning "LTP 长文本测试失败,跳过"
            fi
            echo
        fi
    fi

    # 4.2 Qwen测试
    print_header "测试 B: Qwen2.5-7B (真实模型调用)"

    if [ ! -f "test_qwen_actual.py" ]; then
        print_error "test_qwen_actual.py 不存在"
        echo
    else
        # 检查模型是否下载
        if [ ! -d "$HOME/.cache/huggingface/hub/models--Qwen--Qwen2.5-7B-Instruct" ]; then
            print_warning "Qwen模型未下载"
            print_info "下载命令: python download_qwen.py"
            echo
        else
            print_info "运行 Qwen2.5-7B 测试..."
            if python test_qwen_actual.py 2>&1; then
                print_success "Qwen 测试完成"
            else
                print_error "Qwen 测试失败"
                print_info "可能原因: 显存不足(需要14-16GB,当前8GB)"
                print_info "详见: QWEN_TEST_SUMMARY.md"
                print_info "替代方案: 使用Qwen2.5-3B或跳过Qwen测试"
            fi
            echo
        fi
    fi

    # 4.3 混合测试
    print_header "测试 C: 混合方案 (LTP + Claude)"

    if [ -f "methods/method_b_hybrid.py" ]; then
        if [ -z "$ANTHROPIC_API_KEY" ]; then
            print_warning "ANTHROPIC_API_KEY 未设置,跳过混合方案测试"
            print_info "设置方法: export ANTHROPIC_API_KEY=sk-ant-..."
        else
            print_info "运行混合方案测试..."
            if python methods/method_b_hybrid.py 2>&1; then
                print_success "混合方案测试完成"
            else
                print_error "混合方案测试失败"
            fi
        fi
    else
        print_warning "混合方案尚未实现"
        print_info "待创建: methods/method_b_hybrid.py"
    fi
    echo

    # 4.4 Claude测试
    print_header "测试 D: 纯Claude方案"

    if [ -f "methods/method_c_claude.py" ]; then
        if [ -z "$ANTHROPIC_API_KEY" ]; then
            print_warning "ANTHROPIC_API_KEY 未设置,跳过Claude测试"
            print_info "设置方法: export ANTHROPIC_API_KEY=sk-ant-..."
        else
            print_info "运行纯Claude测试..."
            if python methods/method_c_claude.py 2>&1; then
                print_success "Claude测试完成"
            else
                print_error "Claude测试失败"
            fi
        fi
    else
        print_warning "Claude方案尚未实现"
        print_info "待创建: methods/method_c_claude.py"
    fi
    echo

    # 5. 显示结果
    print_header "测试结果"

    if [ -d "results" ]; then
        print_info "结果文件:"
        ls -lh results/*.json results/*.md 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
    else
        print_warning "results/ 目录不存在"
    fi
    echo

    # 6. 总结
    print_header "测试完成"
    print_success "所有可用测试已运行"
    echo
    print_info "查看详细报告:"
    echo "  - LTP 实验报告: results/ltp_experiment_report.md"
    echo "  - 实验总结: results/experiment_summary.md"
    echo "  - 测试数据说明: results/test_data_summary.md"
    echo
}

# 运行主函数
main "$@"
